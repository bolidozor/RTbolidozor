import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack

from django.urls import path
from . import consumers
from .routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtbolidozor_backend.settings')
django_asgi_app = get_asgi_application()

import rtbolidozor_backend.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        rtbolidozor_backend.routing.websocket_urlpatterns
    ),
})


#application = ProtocolTypeRouter({
#    "http": get_asgi_application(),
#    "websocket": AuthMiddlewareStack(
#        URLRouter(
#            websocket_urlpatterns
#        )
#    ),
#})
