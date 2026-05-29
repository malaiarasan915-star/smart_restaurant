from django.db import models
from django.conf import settings
from apps.menu.models import Dish

class Order(models.Model):
    """
    Represents an order placed by a customer or guest.
    Tracks state machine and payment status.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='orders'
    )
    customer_name = models.CharField(max_length=100, blank=True)  # Used for Guest checkout
    table_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_method = models.CharField(max_length=30, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} (Table {self.table_number})"

class OrderItem(models.Model):
    """
    Represents an individual item line in an Order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    customization = models.CharField(max_length=255, blank=True)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.dish.name} (Order #{self.order.id})"

class Review(models.Model):
    """
    Feedback and ratings left by customers post-delivery.
    """
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order #{self.order.id} - {self.rating} Stars"
