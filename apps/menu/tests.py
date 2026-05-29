from django.test import TestCase
from django.urls import reverse
from apps.menu.models import Category, Dish
from apps.menu.templatetags.menu_extras import mul

class MenuTemplateFilterTests(TestCase):
    def test_mul_filter_valid_integers(self):
        self.assertEqual(mul(5, 4), 20)
        self.assertEqual(mul("5", "4"), 20)

    def test_mul_filter_valid_floats(self):
        self.assertAlmostEqual(mul(5.5, 2), 11)
        self.assertAlmostEqual(mul(1.5, 1.5), 2.25)

    def test_mul_filter_invalid_inputs(self):
        self.assertEqual(mul("invalid", 4), 0)
        self.assertEqual(mul(5, None), 0)


class MenuViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Starters", order=1)
        self.dish1 = Dish.objects.create(
            category=self.category,
            name="Spring Rolls",
            description="Crispy and delicious",
            price=150.00,
            is_available=True,
            is_vegetarian=True
        )
        self.dish2 = Dish.objects.create(
            category=self.category,
            name="Chicken Wings",
            description="Spicy wings",
            price=250.00,
            is_available=False,  # Unavailable
            is_vegetarian=False
        )

    def test_menu_list_view_renders_correctly(self):
        response = self.client.get(reverse('menu:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu/menu.html')
        
        # Only self.dish1 should be in the context and rendered since dish2 is unavailable
        categories = response.context['categories']
        self.assertEqual(categories.count(), 1)
        
        dishes = categories.first().dishes.all()
        self.assertIn(self.dish1, dishes)
        self.assertNotIn(self.dish2, dishes)

    def test_menu_list_view_sets_table_number(self):
        response = self.client.get(reverse('menu:list') + '?table=12')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get('table_number'), 12)
        self.assertEqual(response.context['current_table'], 12)

    def test_dish_detail_view(self):
        response = self.client.get(reverse('menu:detail', args=[self.dish1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['dish'], self.dish1)

    def test_dish_detail_view_not_found_if_unavailable(self):
        response = self.client.get(reverse('menu:detail', args=[self.dish2.id]))
        self.assertEqual(response.status_code, 404)
