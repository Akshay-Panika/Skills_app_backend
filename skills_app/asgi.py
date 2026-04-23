import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # Ye line add karein

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skills_app.settings')

# 1. Pehle HTTP application ko initialize karein
django_asgi_app = get_asgi_application()

# 2. Routing ko initialize karne se pehle imports yahan karein
import chat.routing 

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack( # Auth ke liye ye zaroori hai
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})