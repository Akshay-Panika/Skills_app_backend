from django.urls import path
from .views import CreateChatRoomView, ChatHistoryView, ChatRoomListView

urlpatterns = [
    path("create-room/", CreateChatRoomView.as_view(), name="create-room"),

    path("rooms/<int:user_id>/", ChatRoomListView.as_view(), name="chat-rooms"),

    path("history/<int:room_id>/", ChatHistoryView.as_view(), name="chat-history"),
]