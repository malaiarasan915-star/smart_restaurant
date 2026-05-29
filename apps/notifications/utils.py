from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_order_update(order_id, status, message):
    """
    Utility helper to broadcast real-time order updates to specific order group channels.
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                f"order_{order_id}",
                {
                    'type': 'order_update',
                    'status': status,
                    'message': message,
                }
            )
        except Exception as e:
            # Fallback gracefully if channel layers are misconfigured or inactive
            print(f"Failed to send real-time notification: {e}")
