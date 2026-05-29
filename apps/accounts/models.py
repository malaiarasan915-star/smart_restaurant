from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom user model representing customers and restaurant staff.
    """
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('chef', 'Chef'),
        ('waiter', 'Waiter'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    table_number = models.IntegerField(null=True, blank=True)

    def is_admin_user(self):
        """Check if user has admin role."""
        return self.role == 'admin'

    def is_chef(self):
        """Check if user has chef role."""
        return self.role == 'chef'

    def is_waiter(self):
        """Check if user has waiter role."""
        return self.role == 'waiter'

    def __str__(self):
        return f"{self.username} ({self.role})"
