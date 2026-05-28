# ASGI configuration for the Roommate Finder project.
# This enables both HTTP and WebSocket support for real-time messaging.

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.messaging.routing import websocket_urlpatterns

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create ASGI application that handles both HTTP and WebSocket protocols
application = ProtocolTypeRouter(
    {
        # Handle HTTP requests with Django's standard ASGI application
        "http": get_asgi_application(),
        # Handle WebSocket connections with authentication and custom routing
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),  # Routes defined in messaging app
    }
)
