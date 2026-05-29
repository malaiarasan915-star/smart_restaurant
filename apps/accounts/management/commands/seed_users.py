from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Seeds default users with different roles for testing role-based authentication'

    def handle(self, *args, **options):
        User = get_user_model()
        self.stdout.write(self.style.NOTICE('Seeding default role users...'))

        users_data = [
            {
                'username': 'admin', 
                'password': 'adminpass', 
                'role': 'admin', 
                'is_staff': True, 
                'is_superuser': True
            },
            {
                'username': 'chef', 
                'password': 'chefpass', 
                'role': 'chef', 
                'is_staff': True, 
                'is_superuser': False
            },
            {
                'username': 'waiter', 
                'password': 'waiterpass', 
                'role': 'waiter', 
                'is_staff': True, 
                'is_superuser': False
            },
            {
                'username': 'customer', 
                'password': 'customerpass', 
                'role': 'customer', 
                'is_staff': False, 
                'is_superuser': False
            },
        ]

        for u_info in users_data:
            user, created = User.objects.get_or_create(username=u_info['username'])
            user.role = u_info['role']
            user.is_staff = u_info['is_staff']
            user.is_superuser = u_info['is_superuser']
            user.set_password(u_info['password'])
            user.phone = '1234567890'
            user.save()
            
            status_str = "Created" if created else "Updated/Reset"
            self.stdout.write(self.style.SUCCESS(
                f"{status_str} User: {u_info['username']} | Pass: {u_info['password']} | Role: {u_info['role']}"
            ))

        self.stdout.write(self.style.SUCCESS('Successfully completed user seeding.'))
