from django.urls import re_path
from .consumers import ServiceChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\d+)/$", ServiceChatConsumer.as_asgi()),
]