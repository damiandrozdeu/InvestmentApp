from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import UserProfile, Transaction, Stock
from decimal import Decimal 

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("portfolio"))
        else:
            return render(request, "simulator/login.html", {  
                "message": "Invalid username and/or password."
            })
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
            return render(request, "simulator/register.html", {  
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            UserProfile.objects.create(user=user) 
        except IntegrityError:
            return render(request, "simulator/register.html", { 
                "message": "Username already taken."
            })
        
        login(request, user)
        return HttpResponseRedirect(reverse("portfolio"))
    return render(request, "simulator/register.html")  

@login_required
def portfolio_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=profile)
    return render(request, 'simulator/portfolio.html', {
        'profile': profile,
        'transactions': transactions
    })

@login_required
def transaction_view(request):
    if request.method == 'POST':
        symbol = request.POST['symbol']
        quantity = int(request.POST['quantity'])
        price = Decimal(request.POST['price']) 
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        stock, _ = Stock.objects.get_or_create(symbol=symbol, defaults={'name': symbol})
        total_cost = Decimal(quantity) * price  
        if total_cost > profile.balance:
            return render(request, 'simulator/transaction.html', {'error': 'Insufficient funds'})

        profile.balance -= total_cost  
        profile.save()

        Transaction.objects.create(user=profile, stock=stock, quantity=quantity, price=price, type='BUY')
        return redirect('portfolio')

    return render(request, 'simulator/transaction.html')
