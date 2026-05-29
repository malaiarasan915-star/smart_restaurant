from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.menu.models import Category, Dish
from apps.orders.models import Order, OrderItem, Review

User = get_user_model()

class OrdersViewTests(TestCase):
    def setUp(self):
        # Setup category and dishes
        self.category = Category.objects.create(name="Beverages", order=2)
        self.dish = Dish.objects.create(
            category=self.category,
            name="Mango Lassi",
            price=90.00,
            is_available=True,
            estimated_time=5
        )
        
        # Setup user accounts
        self.customer = User.objects.create_user(
            username="customer_user", password="pwd123password", role="customer"
        )
        self.chef = User.objects.create_user(
            username="chef_user", password="pwd123password", role="chef"
        )
        
        # URLs
        self.cart_url = reverse('orders:cart')
        self.cart_add_url = reverse('orders:cart_add')
        self.cart_remove_url = reverse('orders:cart_remove')
        self.place_order_url = reverse('orders:place_order')
        
    def test_cart_management_api(self):
        """Verify cart session add and remove API views."""
        # 1. Add item to cart via AJAX
        add_data = {'dish_id': self.dish.id, 'quantity': 2, 'customization': 'Less sugar'}
        response = self.client.post(
            self.cart_add_url,
            data=add_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['item_quantity'], 2)
        self.assertEqual(response.json()['cart_count'], 2)

        # 2. Verify cart list page reflects addition
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_amount'], 180.00)

        # 3. Remove/Decrement item from cart via AJAX
        remove_data = {'dish_id': self.dish.id}
        response = self.client.post(
            self.cart_remove_url,
            data=remove_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['item_quantity'], 1)
        self.assertEqual(response.json()['cart_count'], 1)

    def test_place_order_flow(self):
        """Verify standard checkout order creation flow."""
        # Add item to cart first
        self.client.post(
            self.cart_add_url,
            data={'dish_id': self.dish.id, 'quantity': 1},
            content_type='application/json'
        )

        # Post to PlaceOrderView
        checkout_data = {
            'table_number': 12,
            'customer_name': 'Aravind',
            'special_instructions': 'Cold lassi',
            'payment_method': 'cash'
        }
        response = self.client.post(self.place_order_url, checkout_data)
        
        # Verify it redirects to the tracking page for cash payment
        self.assertEqual(response.status_code, 302)
        
        # Verify order exists in DB
        order = Order.objects.latest('id')
        self.assertEqual(order.table_number, 12)
        self.assertEqual(order.total_amount, 90.00)
        self.assertEqual(order.status, 'pending')
        
        # Verify OrderItem exists
        item = order.items.first()
        self.assertEqual(item.dish, self.dish)
        self.assertEqual(item.quantity, 1)

    def test_review_submission(self):
        """Verify rating feedback submissions on completed orders."""
        order = Order.objects.create(
            table_number=4,
            total_amount=90.00,
            status='delivered'
        )
        
        review_url = reverse('orders:review', args=[order.id])
        post_data = {'rating': 5, 'feedback': 'Splendid drink!'}
        
        response = self.client.post(review_url, post_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify review is written
        review = Review.objects.get(order=order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.feedback, 'Splendid drink!')

    def test_chef_status_update_auth(self):
        """Verify only staff accounts can transition order stages."""
        order = Order.objects.create(
            table_number=6,
            total_amount=90.00,
            status='pending'
        )
        
        update_url = reverse('orders:update_status', args=[order.id])
        update_payload = {'status': 'preparing'}

        # Anonymous request -> should redirect to login (auth wrapper check)
        response = self.client.post(
            update_url,
            data=update_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 302)

        # Logged-in Customer -> returns Forbidden 403
        self.client.force_login(self.customer)
        response = self.client.post(
            update_url,
            data=update_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

        # Logged-in Chef -> returns success and transitions state
        self.client.force_login(self.chef)
        response = self.client.post(
            update_url,
            data=update_payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'preparing')
