from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from .models import UserProfile, Stock, Transaction, PendingSell, Favorite, StockHistory
from decimal import Decimal
from django.utils.timezone import now
from django.db.models import Q
import yfinance as yf
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.db import models
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test

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
    profile = UserProfile.objects.get(user=request.user)
    transactions = Transaction.objects.filter(user=profile).order_by('-date')

    holdings = {}
    for transaction in transactions:
        stock = transaction.stock
        symbol = stock.symbol
        if symbol not in holdings:
            holdings[symbol] = {'quantity': 0, 'total_value': 0}
        if transaction.type == 'BUY':
            holdings[symbol]['quantity'] += transaction.quantity
            holdings[symbol]['total_value'] += transaction.quantity * transaction.price
        elif transaction.type == 'SELL':
            holdings[symbol]['quantity'] -= transaction.quantity
            holdings[symbol]['total_value'] -= transaction.quantity * transaction.price

    holdings = {
        k: {
            'quantity': v['quantity'],
            'total_value': v['total_value'],
            'price_per_stock': (v['total_value'] / v['quantity']) if v['quantity'] > 0 else 0
        }
        for k, v in holdings.items() if v['quantity'] > 0
    }

    pending_sells = PendingSell.objects.filter(user=profile)
    for pending_sell in pending_sells:
        pending_sell.time_elapsed = (now() - pending_sell.created_at).total_seconds() // 3600

    if request.method == "POST":
        action = request.POST.get("action")
        amount = Decimal(request.POST.get("amount", 0))

        if action == "add_funds":
            if amount > 0:
                profile.balance += amount
                profile.save()
                messages.success(request, f"Successfully added ${amount:.2f}.")
            else:
                messages.error(request, "Enter a positive amount.")
        elif action == "withdraw_funds":
            if amount > 0 and amount <= profile.balance:
                profile.balance -= amount
                profile.save()
                messages.success(request, f"Successfully withdrew ${amount:.2f}.")
            else:
                messages.error(request, "Invalid withdrawal amount.")

    return render(request, 'simulator/portfolio.html', {
        'profile': profile,
        'transactions': transactions,
        'holdings': holdings,
        'pending_sells': pending_sells,
    })


@login_required
def buy_stock(request, symbol):
    if request.method == 'POST':
        stock = get_object_or_404(Stock, symbol=symbol)
        quantity = int(request.POST['quantity'])
        profile = UserProfile.objects.get(user=request.user)

        total_cost = stock.price * quantity
        if total_cost > profile.balance:
            messages.error(request, "Insufficient balance.")
            return redirect('portfolio')

        profile.balance -= total_cost
        profile.save()

        Transaction.objects.create(user=profile, stock=stock, quantity=quantity, price=stock.price, type='BUY')
        messages.success(request, f"Purchased {quantity} shares of {symbol}.")
        return redirect('portfolio')


@login_required
def sell_now(request, symbol):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity'))

            if quantity <= 0:
                return JsonResponse({'error': "Invalid quantity."}, status=400)

            profile = UserProfile.objects.get(user=request.user)
            stock = Stock.objects.get(symbol=symbol)

            transactions = Transaction.objects.filter(user=profile, stock=stock, type='BUY')
            owned_quantity = sum(t.quantity for t in transactions) - \
                             sum(t.quantity for t in Transaction.objects.filter(user=profile, stock=stock, type='SELL'))

            if quantity > owned_quantity:
                return JsonResponse({'error': "You don't have enough shares to sell."}, status=400)

            total_value = stock.price * quantity * Decimal(0.995)

            profile.balance += total_value
            profile.save()

            Transaction.objects.create(
                user=profile, stock=stock, quantity=quantity, price=stock.price, type='SELL'
            )

            return JsonResponse({'success': f"Successfully sold {quantity} shares of {symbol} for ${total_value:.2f}."})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': "Invalid request method."}, status=405)


@login_required
def wait_and_sell(request, symbol):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_price = Decimal(data.get('target_price'))

            if target_price <= 0:
                return JsonResponse({'error': "Invalid target price."}, status=400)

            stock = Stock.objects.get(symbol=symbol)
            profile = UserProfile.objects.get(user=request.user)

            PendingSell.objects.create(user=profile, stock=stock, target_price=target_price)

            return JsonResponse({'success': f"Pending sell for {symbol} at ${target_price:.2f} has been created."})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': "Invalid request method."}, status=405)


@login_required
def cancel_pending_sell(request, sell_id):
    if request.method == 'POST':
        try:
            pending_sell = get_object_or_404(PendingSell, id=sell_id, user__user=request.user)
            pending_sell.delete()
            return JsonResponse({'success': "Pending sell has been canceled."})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': "Invalid request method."}, status=405)



def market_view(request):
    profile = None
    user_favorites = []
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        user_favorites = Favorite.objects.filter(user=profile).values_list('stock__symbol', flat=True)

    sectors = Stock.objects.values_list('sector', flat=True).distinct()
    stocks = Stock.objects.all()
    search = request.GET.get('search', '')
    sector = request.GET.get('sector', '')

    if search:
        stocks = stocks.filter(Q(symbol__icontains=search) | Q(name__icontains=search))
    if sector:
        stocks = stocks.filter(sector=sector)

    stocks_data = []
    for stock in stocks:
        history = stock.history.order_by('date')[:30]  
        dates = [h.date.strftime('%Y-%m-%d') for h in history] 
        prices = [float(h.close_price) for h in history]

        stocks_data.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "price": str(stock.price),
            "sector": stock.sector,
            "history": {
                "dates": dates,
                "prices": prices,
            },
        })

    return render(request, 'simulator/market.html', {
        'stocks': stocks,
        'sectors': sectors,
        'stocks_json': json.dumps(stocks_data),
        'user_favorites': list(user_favorites),
    })



@login_required
def stock_details(request, symbol):
    try:
        stock = get_object_or_404(Stock, symbol=symbol)
        data = {
            'name': stock.name,
            'sector': stock.sector,
            'market_cap': stock.market_cap, 
            'current_price': str(stock.price),
            'last_updated': stock.last_updated.strftime('%Y-%m-%d %H:%M:%S'),
        }
        history = stock.history.all()
        if history.exists():
            data['high_52_week'] = str(history.aggregate(models.Max('close_price'))['close_price__max'])
            data['low_52_week'] = str(history.aggregate(models.Min('close_price'))['close_price__min'])
            data['volume'] = history.latest('date').volume
        else:
            data['high_52_week'] = data['low_52_week'] = data['volume'] = None

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
@login_required
def toggle_favorite(request, symbol):
    if request.method == 'POST':
        stock = get_object_or_404(Stock, symbol=symbol)
        profile = UserProfile.objects.get(user=request.user)

        favorite, created = Favorite.objects.get_or_create(user=profile, stock=stock)
        if not created:
            favorite.delete()
            return JsonResponse({'success': f'{symbol} removed from favorites.', 'action': 'removed'})
        return JsonResponse({'success': f'{symbol} added to favorites.', 'action': 'added'})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def favorites_view(request):
    profile = UserProfile.objects.get(user=request.user)
    favorites = Favorite.objects.filter(user=profile).select_related('stock')
    return render(request, 'simulator/favorites.html', {
        'favorites': favorites,
    })
@login_required
def update_stock_prices(request):
    if not request.user.is_staff:  
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    stocks = Stock.objects.all()
    updated_stocks = []
    for stock in stocks:
        try:
            
            stock_data = yf.Ticker(stock.symbol)  
            current_price = stock_data.info['currentPrice'] 
            stock.price = current_price
            stock.last_updated = now()
            stock.save()
            updated_stocks.append(stock.symbol)
        except Exception as e:
            print(f"Error updating {stock.symbol}: {e}")

    return JsonResponse({'updated_stocks': updated_stocks})


def update_stock_prices():
    stocks = Stock.objects.all()
    updated_stocks = []

    for stock in stocks:
        try:
            stock_data = yf.Ticker(stock.symbol)

            current_price = stock_data.info.get('currentPrice')
            if current_price:
                stock.price = current_price
                stock.last_updated = now()
                stock.save()

            StockHistory.objects.filter(stock=stock).delete()

            start_date = (datetime.now() - timedelta(days=30)).date()
            end_date = datetime.now().date()

            hist = stock_data.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

            if not hist.empty:
                for date, row in hist.iterrows():
                    close_price = row.get('Close')
                    volume = row.get('Volume', 0)

                    if close_price is not None:
                        StockHistory.objects.create(
                            stock=stock,
                            date=date,
                            close_price=close_price,
                            volume=volume
                        )

            updated_stocks.append(stock.symbol)
            print(f"Updated {stock.symbol}")

        except Exception as e:
            print(f"Error updating {stock.symbol}: {e}")

    return updated_stocks


@login_required
@user_passes_test(lambda u: u.is_staff) 
def trigger_stock_update(request):
    try:
        updated_stocks = update_stock_prices()
        return JsonResponse({'success': True, 'updated_stocks': updated_stocks})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

