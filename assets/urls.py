from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.orders_view, name='orders'),
    path('initiate-order/', views.initiate_order, name='initiate_order'),
    path('portfolio/', views.portfolio_view, name='portfolio'),
]