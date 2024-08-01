# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("rtmap_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("rtmap_group", self.channel_name)

    async def bz_event(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def receive(self, text_data):
        #message = json.loads(text_data).get('message')
        message = text_data
        await self.channel_layer.group_send(
            "rtmap_group",
            {
                'type': 'bz_event',
                'message': message
            }
        )