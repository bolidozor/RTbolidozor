# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'rtmap_group'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECED CODE: ",code)

    def receive(self, text_data=None, bytes_data=None):
        print(" MESSAGE RECEIVED")
        data = json.loads(text_data)
        message = data['message']
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, 
            {
                "type": 'chat_message',
                "message": message
            }
        )
    def chat_message(self, event):
        print("EVENT TRIGERED")
        # Receive message from room group
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))
