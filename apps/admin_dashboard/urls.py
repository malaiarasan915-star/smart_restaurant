from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('api/orders/', views.OrderApiView.as_view(), name='order_api'),
    path('menu/', views.MenuManagementView.as_view(), name='menu'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('tables/', views.TableManagementView.as_view(), name='tables'),
]
