import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from apps.accounts.decorators import role_required
from apps.orders.models import Order, OrderItem
from apps.menu.models import Category, Dish
from apps.menu.utils import generate_table_qr

class DashboardHomeView(LoginRequiredMixin, View):
    """
    Admin dashboard home rendering statistics and mounting live orders table.
    """
    @method_decorator(role_required('admin'))
    def get(self, request):
        today = timezone.localdate()
        today_start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        today_end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

        orders_today = Order.objects.filter(created_at__range=(today_start, today_end))
        
        total_orders = orders_today.count()
        total_revenue = orders_today.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        pending_orders = orders_today.filter(status='pending').count()
        delivered_orders = orders_today.filter(status='delivered').count()

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders
        }
        return render(request, 'admin_dashboard/home.html', context)

class OrderApiView(LoginRequiredMixin, View):
    """
    REST JSON endpoint returning active orders for the LiveOrdersTable React component.
    """
    @method_decorator(role_required(['admin', 'chef', 'waiter']))
    def get(self, request):
        active_orders = Order.objects.exclude(
            status__in=['delivered', 'cancelled']
        ).prefetch_related('items__dish').order_by('-created_at')
        
        orders_data = []
        for order in active_orders:
            orders_data.append({
                'id': order.id,
                'table_number': order.table_number,
                'item_count': sum(item.quantity for item in order.items.all()),
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })
        return JsonResponse(orders_data, safe=False)

class MenuManagementView(LoginRequiredMixin, View):
    """
    Admin menu CRUD page (view/add/delete dishes).
    """
    @method_decorator(role_required('admin'))
    def get(self, request):
        categories = Category.objects.all().order_by('order')
        dishes = Dish.objects.select_related('category').all().order_by('category__order', 'name')
        return render(request, 'admin_dashboard/menu.html', {
            'categories': categories,
            'dishes': dishes
        })

    @method_decorator(role_required('admin'))
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'add_dish':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            price = request.POST.get('price')
            category_id = request.POST.get('category_id')
            is_veg = request.POST.get('is_vegetarian') == 'true'
            estimated_time = request.POST.get('estimated_time', 15)
            image = request.FILES.get('image')

            category = get_object_or_404(Category, id=category_id)
            
            Dish.objects.create(
                category=category,
                name=name,
                description=description,
                price=price,
                is_vegetarian=is_veg,
                estimated_time=estimated_time,
                image=image
            )
            messages.success(request, f"Dish '{name}' created successfully!")
            
        elif action == 'delete_dish':
            dish_id = request.POST.get('dish_id')
            dish = get_object_or_404(Dish, id=dish_id)
            dish.delete()
            messages.success(request, "Dish deleted successfully.")

        return redirect('admin_dashboard:menu')

class AnalyticsView(LoginRequiredMixin, View):
    """
    Render analytical trends dashboard using Chart.js templates.
    """
    @method_decorator(role_required('admin'))
    def get(self, request):
        last_7_days = []
        revenue_by_day = []
        today = timezone.localdate()
        
        for i in range(6, -1, -1):
            day = today - datetime.timedelta(days=i)
            day_start = timezone.make_aware(datetime.datetime.combine(day, datetime.time.min))
            day_end = timezone.make_aware(datetime.datetime.combine(day, datetime.time.max))
            
            day_rev = Order.objects.filter(
                created_at__range=(day_start, day_end),
                payment_status='paid'
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            last_7_days.append(day.strftime('%a'))
            revenue_by_day.append(float(day_rev))

        # Top dishes
        top_dishes = OrderItem.objects.values('dish__name').annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:5]
        
        top_dish_names = [item['dish__name'] for item in top_dishes]
        top_dish_qtys = [int(item['total_qty']) for item in top_dishes]

        # Order status distribution
        status_counts = Order.objects.values('status').annotate(count=Count('id'))
        status_labels = [item['status'].capitalize() for item in status_counts]
        status_values = [item['count'] for item in status_counts]

        context = {
            'chart_days': json.dumps(last_7_days),
            'chart_revenue': json.dumps(revenue_by_day),
            'top_dish_names': json.dumps(top_dish_names),
            'top_dish_qtys': json.dumps(top_dish_qtys),
            'status_labels': json.dumps(status_labels),
            'status_values': json.dumps(status_values),
        }
        return render(request, 'admin_dashboard/analytics.html', context)

class TableManagementView(LoginRequiredMixin, View):
    """
    Manage QR codes and generate tables.
    """
    @method_decorator(role_required('admin'))
    def get(self, request):
        tables = list(range(1, 21))
        return render(request, 'admin_dashboard/tables.html', {'tables': tables})

    @method_decorator(role_required('admin'))
    def post(self, request):
        table_number = request.POST.get('table_number')
        if table_number:
            generate_table_qr(table_number)
            messages.success(request, f"QR code for Table {table_number} generated successfully.")
        return redirect('admin_dashboard:tables')
