from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from apps.accounts.decorators import role_required
from apps.orders.models import Order

class KitchenDashboardView(LoginRequiredMixin, View):
    """
    Renders the kitchen cooking board dashboard.
    """
    @method_decorator(role_required(['admin', 'chef']))
    def get(self, request):
        return render(request, 'kitchen/dashboard.html')

class KitchenOrderApiView(LoginRequiredMixin, View):
    """
    JSON API endpoint returning orders with state 'confirmed' or 'preparing'.
    Used by the React KitchenBoard component.
    """
    @method_decorator(role_required(['admin', 'chef']))
    def get(self, request):
        orders = Order.objects.filter(
            status__in=['confirmed', 'preparing']
        ).prefetch_related('items__dish').order_by('created_at')

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
                'created_at': order.created_at.isoformat(),
                'special_instructions': order.special_instructions,
                'status': order.status,
                'items': items_data
            })
        return JsonResponse(orders_data, safe=False)
