from django.urls import re_path
from .consumers import RoomListConsumer, ServiceChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\d+)/$", ServiceChatConsumer.as_asgi()),

    # 🔥 NEW ROOM LIST SOCKET
    re_path(r"ws/user/(?P<user_id>\d+)/rooms/$", RoomListConsumer.as_asgi()),
]