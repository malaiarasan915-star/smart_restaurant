from django.urls import path
from . import views

app_name = 'supplier'

urlpatterns = [
    path('', views.SupplierDashboardView.as_view(), name='dashboard'),
    path('api/orders/', views.SupplierOrderApiView.as_view(), name='order_api'),
]
