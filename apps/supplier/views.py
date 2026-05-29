from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from apps.accounts.decorators import role_required
from apps.orders.models import Order

class SupplierDashboardView(LoginRequiredMixin, View):
    """
    Renders the waiter/supplier dashboard page.
    """
    @method_decorator(role_required(['admin', 'waiter']))
    def get(self, request):
        return render(request, 'supplier/dashboard.html')

class SupplierOrderApiView(LoginRequiredMixin, View):
    """
    JSON API returning orders with status 'ready' for the waiter board.
    """
    @method_decorator(role_required(['admin', 'waiter']))
    def get(self, request):
        orders = Order.objects.filter(status='ready').prefetch_related('items__dish').order_by('-updated_at')
        
        orders_data = []
        for order in orders:
            items_data = []
            for item in order.items.all():
                items_data.append({
                    'id': item.id,
                    'dish_name': item.dish.name,
                    'quantity': item.quantity,
                    'customization': item.customization
                })
            orders_data.append({
                'id': order.id,
                'table_number': order.table_number,
                'status': order.status,
                'payment_status': order.payment_status,
                'customer_name': order.customer_name,
                'items': items_data
            })
        return JsonResponse(orders_data, safe=False)
