from django.test import TestCase
from apps.notifications.utils import notify_order_update

class NotificationsTests(TestCase):
    def test_notify_order_update_runs(self):
        """Verify that notify_order_update function executes without throwing exceptions."""
        try:
            notify_order_update(order_id=1, status='preparing', message='Your food is cooking!')
            executed_successfully = True
        except Exception as e:
            executed_successfully = False
            
        self.assertTrue(executed_successfully)
