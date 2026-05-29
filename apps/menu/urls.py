from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.MenuListView.as_view(), name='list'),
    path('dish/<int:pk>/', views.DishDetailView.as_view(), name='detail'),
    path('toggle-availability/', views.ToggleDishAvailabilityView.as_view(), name='toggle_availability'),
]
