from django.db import models

class Category(models.Model):
    """
    Represents menu categories (e.g. Starters, Main Course, Desserts, Beverages).
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class name, e.g. bi-cup-hot")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Dish(models.Model):
    """
    Represents individual menu items/dishes.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    estimated_time = models.IntegerField(default=15, help_text='Estimated cook time in minutes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name
