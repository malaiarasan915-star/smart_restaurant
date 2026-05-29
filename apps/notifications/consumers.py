import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrderNotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer handling real-time WebSocket order tracking updates.
    """
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.group_name = f"order_{self.order_id}"

        # Join the order specific channel group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the order group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def order_update(self, event):
        """
        Receives updates from channel group and pushes down to clients.
        """
        status = event['status']
        message = event['message']

        # Send status update message to WebSocket client
        await self.send(text_data=json.dumps({
            'status': status,
            'message': message,
        }))
