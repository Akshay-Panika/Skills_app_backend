from django.urls import path
from .views import ChatMessagesView, UserChatsView

urlpatterns = [
    path("chat/messages/<int:chat_room_id>/", ChatMessagesView.as_view()),
    path("chat/user/<int:user_id>/", UserChatsView.as_view()),
]