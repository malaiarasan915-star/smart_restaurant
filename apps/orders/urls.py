from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/remove/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart/quantity/', views.CartQtyView.as_view(), name='cart_quantity'),
    path('place-order/', views.PlaceOrderView.as_view(), name='place_order'),
    path('tracking/<int:order_id>/', views.OrderTrackingView.as_view(), name='tracking'),
    path('<int:order_id>/status/', views.OrderStatusView.as_view(), name='status'),
    path('history/', views.OrderHistoryView.as_view(), name='history'),
    path('review/<int:order_id>/', views.ReviewView.as_view(), name='review'),
    path('<int:order_id>/update-status/', views.UpdateOrderStatusView.as_view(), name='update_status'),
]
