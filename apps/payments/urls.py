from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:order_id>/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<int:order_id>/', views.PaymentSuccessView.as_view(), name='success'),
]
