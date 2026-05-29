from django.urls import path
from . import views

app_name = 'kitchen'

urlpatterns = [
    path('', views.KitchenDashboardView.as_view(), name='dashboard'),
    path('api/orders/', views.KitchenOrderApiView.as_view(), name='order_api'),
]
