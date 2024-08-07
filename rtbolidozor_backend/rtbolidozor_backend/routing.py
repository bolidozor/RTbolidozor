from django.urls import path
from . import consumers

websocket_urlpatterns = [
#    path('/', consumers.ChatConsumer.as_asgi()),
    path('ws/', consumers.ChatConsumer.as_asgi())
]
