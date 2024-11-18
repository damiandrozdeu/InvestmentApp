from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_view, name='portfolio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('market/', views.market_view, name='market'),
    path('buy/<str:symbol>/', views.buy_stock, name='buy_stock'),
    path('sell-now/<str:symbol>/', views.sell_now, name='sell_now'), 
    path('wait-and-sell/<str:symbol>/', views.wait_and_sell, name='wait_and_sell'),
    path('cancel-pending-sell/<int:sell_id>/', views.cancel_pending_sell, name='cancel_pending_sell'),
    path('stock-details/<str:symbol>/', views.stock_details, name='stock_details'),
    path('favorites/', views.favorites_view, name='favorites'),  
    path('toggle-favorite/<str:symbol>/', views.toggle_favorite, name='toggle_favorite'),
    path('stock-admin/update-stocks/', views.trigger_stock_update, name='update_stocks'),

  

]
