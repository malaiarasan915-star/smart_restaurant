import json
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from apps.accounts.decorators import role_required
from .models import Category, Dish

class MenuListView(ListView):
    """
    Public digital menu list. Filters categories and available dishes.
    Saves the table number to the session if accessed via QR (?table=N).
    """
    model = Category
    template_name = 'menu/menu.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Prefetch related dishes to avoid N+1 query issue, showing only available dishes.
        from django.db.models import Prefetch
        return Category.objects.prefetch_related(
            Prefetch('dishes', queryset=Dish.objects.filter(is_available=True))
        ).order_by('order')

    def get(self, request, *args, **kwargs):
        table_param = request.GET.get('table')
        if table_param:
            try:
                request.session['table_number'] = int(table_param)
            except ValueError:
                pass
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_table'] = self.request.session.get('table_number')
        return context

class DishDetailView(DetailView):
    """
    Displays details of an individual dish.
    """
    model = Dish
    template_name = 'menu/detail.html'
    context_object_name = 'dish'

    def get_queryset(self):
        return Dish.objects.select_related('category').filter(is_available=True)

class ToggleDishAvailabilityView(LoginRequiredMixin, View):
    """
    AJAX view to toggle the availability of a dish. Restricted to Admin role.
    """
    @method_decorator(role_required('admin'))
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            dish_id = data.get('dish_id')
            dish = get_object_or_404(Dish, id=dish_id)
            dish.is_available = not dish.is_available
            dish.save()
            return JsonResponse({
                'success': True, 
                'dish_id': dish.id, 
                'is_available': dish.is_available
            })
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'error': 'Invalid request body.'}, status=400)
