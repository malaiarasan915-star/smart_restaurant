from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.menu.models import Category, Dish
from apps.orders.models import Order

User = get_user_model()

class AdminDashboardTests(TestCase):
    def setUp(self):
        # Create categories and dishes
        self.category = Category.objects.create(name="Sides", order=3)
        self.dish = Dish.objects.create(
            category=self.category,
            name="Garlic Bread",
            price=120.00,
            is_available=True
        )

        # Setup standard accounts
        self.admin_user = User.objects.create_user(
            username="admin_user", password="pwd123password", role="admin"
        )
        self.customer = User.objects.create_user(
            username="customer_user", password="pwd123password", role="customer"
        )

        # Create active order
        self.order = Order.objects.create(
            table_number=5,
            total_amount=120.00,
            status='pending',
            payment_status='paid'
        )

        # URLs
        self.home_url = reverse('admin_dashboard:home')
        self.api_orders_url = reverse('admin_dashboard:order_api')
        self.menu_url = reverse('admin_dashboard:menu')
        self.analytics_url = reverse('admin_dashboard:analytics')
        self.tables_url = reverse('admin_dashboard:tables')

    def test_dashboard_access_control(self):
        """Verify that anonymous and customer users are blocked from admin home."""
        # 1. Anonymous -> redirects to login
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)

        # 2. Customer -> forbidden 403
        self.client.force_login(self.customer)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 403)

        # 3. Admin -> success 200
        self.client.force_login(self.admin_user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard/home.html')
        self.assertEqual(response.context['total_orders'], 1)
        self.assertEqual(response.context['total_revenue'], 120.00)

    def test_active_orders_api(self):
        """Verify the active orders API serialized response."""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.api_orders_url)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['table_number'], 5)
        self.assertEqual(data[0]['status'], 'pending')

    def test_menu_management_crud(self):
        """Verify adding and deleting dishes through admin panel."""
        self.client.force_login(self.admin_user)

        # 1. Add Dish
        post_data = {
            'action': 'add_dish',
            'name': 'French Fries',
            'description': 'Salted French fries',
            'price': '100.00',
            'category_id': self.category.id,
            'is_vegetarian': 'true',
            'estimated_time': '10'
        }
        response = self.client.post(self.menu_url, post_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify French Fries is created
        fries = Dish.objects.get(name='French Fries')
        self.assertEqual(fries.price, 100.00)
        self.assertTrue(fries.is_vegetarian)

        # 2. Delete Dish
        delete_data = {
            'action': 'delete_dish',
            'dish_id': fries.id
        }
        response = self.client.post(self.menu_url, delete_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify French Fries is deleted
        with self.assertRaises(Dish.DoesNotExist):
            Dish.objects.get(name='French Fries')

    def test_analytics_charts_context(self):
        """Verify analytics charts load appropriate JSON context elements."""
        self.client.force_login(self.admin_user)
        response = self.client.get(self.analytics_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('chart_days', response.context)
        self.assertIn('chart_revenue', response.context)
