from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import UserProfile, Stock, Transaction, PendingSell
from decimal import Decimal
from django.utils.timezone import now
import yfinance as yf
from django.contrib import messages
from collections import defaultdict
import json


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("portfolio"))
        else:
            return render(request, "simulator/login.html", {"message": "Invalid username and/or password."})
    return render(request, "simulator/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "simulator/register.html", {"message": "Passwords must match."})

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            UserProfile.objects.create(user=user)
        except IntegrityError:
            return render(request, "simulator/register.html", {"message": "Username already taken."})

        login(request, user)
        return HttpResponseRedirect(reverse("portfolio"))
    return render(request, "simulator/register.html")


@login_required
def portfolio_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=profile).order_by('-date')

    holdings = defaultdict(lambda: {'quantity': 0, 'total_value': 0})
    for transaction in transactions:
        stock = transaction.stock
        if transaction.type == 'BUY':
            holdings[stock.symbol]['quantity'] += transaction.quantity
            holdings[stock.symbol]['total_value'] += transaction.quantity * transaction.price
        elif transaction.type == 'SELL':
            holdings[stock.symbol]['quantity'] -= transaction.quantity
            holdings[stock.symbol]['total_value'] -= transaction.quantity * transaction.price

    holdings = {k: v for k, v in holdings.items() if v['quantity'] > 0}

    pending_sells = PendingSell.objects.filter(user=profile)
    for pending_sell in pending_sells:
        pending_sell.time_elapsed = (now() - pending_sell.created_at).total_seconds() // 3600  # in hours

    message = None
    message_class = None

    if request.method == "POST":
        action = request.POST.get("action")
        amount = Decimal(request.POST.get("amount", 0))

        if action == "add_funds":
            if amount > 0:
                profile.balance += amount
                profile.save()
                messages.success(request, f"Successfully added ${amount:.2f} to your balance.")
            else:
                messages.error(request, "Invalid amount. Please enter a positive value.")

        elif action == "withdraw_funds":
            if amount > 0 and amount <= profile.balance:
                profile.balance -= amount
                profile.save()
                messages.success(request, f"Successfully withdrew ${amount:.2f} from your balance.")
            elif amount > profile.balance:
                messages.error(request, "Insufficient funds to withdraw the requested amount.")
            else:
                messages.error(request, "Invalid amount. Please enter a positive value.")

    return render(request, 'simulator/portfolio.html', {
        'profile': profile,
        'transactions': transactions,
        'holdings': holdings,
        'pending_sells': pending_sells,
    })


def market_view(request):
    symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NFLX", "NVDA", "BRK-B", "V", 
        "JPM", "JNJ", "XOM", "PG", "UNH", "HD", "MA", "PFE", "KO", "PEP", 
        "DIS", "BAC", "VZ", "CSCO", "ADBE", "CRM", "CMCSA", "INTC", "T", "WMT"
    ]

    for symbol in symbols:
        try:
            stock_data = yf.Ticker(symbol)
            stock_info = stock_data.info
            current_price = stock_info.get('currentPrice', None)

            if current_price is not None:
                Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={
                        'name': stock_info.get('shortName', 'N/A'),
                        'price': current_price,
                        'market_cap': stock_info.get('marketCap', None),
                        'sector': stock_info.get('sector', 'N/A'),
                    }
                )
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    stocks = Stock.objects.all()
    return render(request, 'simulator/market.html', {'stocks': stocks})


@login_required
def buy_stock(request, symbol):
    if request.method == 'POST':
        stock = get_object_or_404(Stock, symbol=symbol)
        quantity = int(request.POST['quantity'])
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        total_cost = stock.price * quantity
        if total_cost > profile.balance:
            messages.error(request, f"Insufficient funds to purchase {quantity} shares of {symbol}.")
            return redirect('market')

        profile.balance -= total_cost
        profile.save()

        Transaction.objects.create(
            user=profile,
            stock=stock,
            quantity=quantity,
            price=stock.price,
            type='BUY'
        )

        messages.success(request, f"Successfully purchased {quantity} shares of {symbol} for ${total_cost:.2f}.")
        return redirect('market')


@login_required
def sell_stock_now(request, symbol):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        stock = Stock.objects.get(symbol=symbol)
        quantity = Decimal(request.POST.get('quantity', 0))

        if quantity <= 0:
            messages.error(request, "Invalid quantity.")
            return redirect('portfolio')

        holdings = Transaction.objects.filter(user=profile, stock=stock, type="BUY")
        owned_quantity = sum(t.quantity for t in holdings)

        if quantity > owned_quantity:
            messages.error(request, "You do not own enough shares to complete this sale.")
            return redirect('portfolio')

        price = stock.price * Decimal(0.995)
        total_value = quantity * price

        profile.balance += total_value
        profile.save()

        Transaction.objects.create(
            user=profile,
            stock=stock,
            quantity=quantity,
            price=price,
            type='SELL'
        )

        messages.success(request, f"Sold {quantity} shares of {symbol} for ${total_value:.2f}")
        return redirect('portfolio')


@login_required
def wait_and_sell(request, symbol):
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            stock = Stock.objects.get(symbol=symbol)
            data = json.loads(request.body)
            target_price = Decimal(data.get('target_price'))

            if target_price <= stock.price:
                messages.error(request, "Target price must be higher than the current price.")
                return redirect('portfolio')

            PendingSell.objects.create(user=profile, stock=stock, target_price=target_price)
            messages.success(request, f"Request to sell {symbol} at ${target_price:.2f} has been added. Minimum wait time: 48 hours.")
            return redirect('portfolio')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('portfolio')
    messages.error(request, "Invalid request method.")
    return redirect('portfolio')
