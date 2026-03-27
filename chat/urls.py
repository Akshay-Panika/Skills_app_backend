from django.urls import path
from .views import ChatMessagesView, UserChatsView, CreateChatRoomView

urlpatterns = [
    path("chat/messages/<int:chat_room_id>/", ChatMessagesView.as_view()),
    path("chat/user/<int:user_id>/", UserChatsView.as_view()),
    path("chat/create/", CreateChatRoomView.as_view()),
]