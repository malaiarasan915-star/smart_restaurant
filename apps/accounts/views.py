from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomUserCreationForm

class CustomerSignUpView(CreateView):
    """
    View for self-registration of customers.
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        messages.success(self.request, 'Registration successful! You can now log in.')
        return super().form_valid(form)

class CustomLoginView(LoginView):
    """
    Login view that redirects the user based on their specific role.
    """
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        role = user.role
        
        if role == 'admin':
            return reverse_lazy('admin_dashboard:home')
        elif role == 'chef':
            return reverse_lazy('kitchen:dashboard')
        elif role == 'waiter':
            return reverse_lazy('supplier:dashboard')
        else:
            table = self.request.session.get('table_number')
            if table:
                return f'/menu/?table={table}'
            return reverse_lazy('menu:list')

def logout_view(request):
    """
    Handles logging out the user.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')
