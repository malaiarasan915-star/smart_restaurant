from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsViewTests(TestCase):
    def setUp(self):
        self.signup_url = reverse('accounts:signup')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.test_username = 'test_diner'
        self.test_password = 'TestPassword123!'
        self.test_phone = '1234567890'

    def test_signup_page_loads(self):
        """Verify the signup view renders correctly on GET."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_customer_registration_success(self):
        """Verify new customer creation and automatic 'customer' role assignment."""
        data = {
            'username': self.test_username,
            'password': self.test_password,
            'phone': self.test_phone,
        }
        # In Django UserCreationForm, we must supply password1 and password2 for validation
        post_data = {
            'username': self.test_username,
            'phone': self.test_phone,
            'password1': self.test_password,
            'password2': self.test_password,
        }
        response = self.client.post(self.signup_url, post_data)
        # Should redirect to login page upon success
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

        # Verify database record exists with correct role
        user = User.objects.get(username=self.test_username)
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.phone, self.test_phone)

    def test_login_and_logout_flow(self):
        """Verify logging in redirect logic and session logout."""
        # Create standard customer user
        user = User.objects.create_user(
            username=self.test_username,
            password=self.test_password,
            role='customer'
        )

        # Get login page
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        # Perform login post
        login_data = {
            'username': self.test_username,
            'password': self.test_password,
        }
        response = self.client.post(self.login_url, login_data)
        # Should login and redirect to default menu list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('menu:list'))

        # Perform logout
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
