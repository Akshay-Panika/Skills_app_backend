from django.urls import path
from .views import (
    RequestServiceChatView,
    UserChatListView,
    ChatRoomDetailView,
    ChatMessageListView,
    SendMessageView,
)

urlpatterns = [
    path("chat/request/<int:service_id>/", RequestServiceChatView.as_view(), name="request-chat"),
    path("chat/user/<int:user_id>/", UserChatListView.as_view(), name="user-chats"),
    path("chat/room/<int:room_id>/", ChatRoomDetailView.as_view(), name="room-detail"),
    path("chat/room/<int:room_id>/messages/", ChatMessageListView.as_view(), name="room-messages"),
    path("chat/room/<int:room_id>/send/", SendMessageView.as_view(), name="send-message"),
]