from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.menu.models import Category, Dish
from apps.orders.models import Order, OrderItem

User = get_user_model()

class KitchenDashboardTests(TestCase):
    def setUp(self):
        # Create category and dish
        self.category = Category.objects.create(name="Desserts", order=4)
        self.dish = Dish.objects.create(
            category=self.category,
            name="Gulab Jamun",
            price=60.00,
            is_available=True
        )

        # Setup standard accounts
        self.chef_user = User.objects.create_user(
            username="chef_user", password="pwd123password", role="chef"
        )
        self.customer = User.objects.create_user(
            username="customer_user", password="pwd123password", role="customer"
        )

        # Create active confirmed order (which shows in kitchen KDS)
        self.order = Order.objects.create(
            table_number=2,
            total_amount=120.00,
            status='confirmed'
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            dish=self.dish,
            quantity=2,
            unit_price=60.00
        )

        # URLs
        self.dashboard_url = reverse('kitchen:dashboard')
        self.api_orders_url = reverse('kitchen:order_api')

    def test_kitchen_dashboard_access_control(self):
        """Verify that anonymous and customer users are blocked from kitchen dashboard."""
        # 1. Anonymous -> redirects to login
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

        # 2. Customer -> forbidden 403
        self.client.force_login(self.customer)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 403)

        # 3. Chef -> success 200
        self.client.force_login(self.chef_user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kitchen/dashboard.html')

    def test_kitchen_order_api(self):
        """Verify the kitchen active orders API returns confirmed/preparing orders."""
        self.client.force_login(self.chef_user)
        response = self.client.get(self.api_orders_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['table_number'], 2)
        self.assertEqual(data[0]['status'], 'confirmed')
        self.assertEqual(len(data[0]['items']), 1)
        self.assertEqual(data[0]['items'][0]['dish_name'], 'Gulab Jamun')
        self.assertEqual(data[0]['items'][0]['quantity'], 2)
