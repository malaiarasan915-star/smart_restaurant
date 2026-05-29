from django.core.management.base import BaseCommand
from apps.menu.models import Category, Dish

class Command(BaseCommand):
    help = 'Seeds the database with sample categories and dishes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding categories and dishes...'))

        # Define Categories
        categories_data = [
            {'name': 'Starters', 'icon': 'bi-egg', 'order': 1},
            {'name': 'Main Course', 'icon': 'bi-egg-fried', 'order': 2},
            {'name': 'Biryani & Rice', 'icon': 'bi-fire', 'order': 3},
            {'name': 'Breads', 'icon': 'bi-disc', 'order': 4},
            {'name': 'Desserts', 'icon': 'bi-cake2', 'order': 5},
            {'name': 'Beverages', 'icon': 'bi-cup-hot', 'order': 6},
        ]

        categories = {}
        for cat_info in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_info['name'],
                defaults={'icon': cat_info['icon'], 'order': cat_info['order']}
            )
            categories[cat_info['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat.name}"))

        # Define Dishes
        dishes_data = [
            {
                'category': 'Starters',
                'name': 'Paneer Tikka',
                'description': 'Marinated paneer cubes grilled to perfection with onions and bell peppers.',
                'price': 180.00,
                'is_vegetarian': True,
                'estimated_time': 15,
            },
            {
                'category': 'Biryani & Rice',
                'name': 'Chicken Biryani',
                'description': 'Fragrant basmati rice layered with juicy chicken marinated in aromatic spices.',
                'price': 280.00,
                'is_vegetarian': False,
                'estimated_time': 25,
            },
            {
                'category': 'Main Course',
                'name': 'Dal Makhani',
                'description': 'Slow-cooked black lentils and kidney beans in a rich, creamy, buttery gravy.',
                'price': 160.00,
                'is_vegetarian': True,
                'estimated_time': 20,
            },
            {
                'category': 'Breads',
                'name': 'Butter Naan',
                'description': 'Soft and fluffy leavened flatbread brushed with generous butter, baked in tandoor.',
                'price': 40.00,
                'is_vegetarian': True,
                'estimated_time': 10,
            },
            {
                'category': 'Desserts',
                'name': 'Gulab Jamun',
                'description': 'Traditional warm milk-solid dumplings dipped in sweet cardamom-infused sugar syrup.',
                'price': 80.00,
                'is_vegetarian': True,
                'estimated_time': 5,
            },
            {
                'category': 'Beverages',
                'name': 'Mango Lassi',
                'description': 'Creamy yogurt beverage blended with sweet ripe mango pulp and cardamom.',
                'price': 90.00,
                'is_vegetarian': True,
                'estimated_time': 5,
            },
        ]

        for dish_info in dishes_data:
            cat = categories[dish_info['category']]
            dish, created = Dish.objects.get_or_create(
                name=dish_info['name'],
                defaults={
                    'category': cat,
                    'description': dish_info['description'],
                    'price': dish_info['price'],
                    'is_vegetarian': dish_info['is_vegetarian'],
                    'estimated_time': dish_info['estimated_time'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created dish: {dish.name}"))

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with menu sample.'))
