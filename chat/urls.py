from django.urls import path
from .views import CreateChatRoomView, ChatHistoryView, ChatRoomListView, DeleteChatRoomView

urlpatterns = [
    path("chat/create-room/", CreateChatRoomView.as_view(), name="create-room"),

    path("chat/rooms/<int:user_id>/", ChatRoomListView.as_view(), name="chat-rooms"),

    path("chat/history/<int:room_id>/", ChatHistoryView.as_view(), name="chat-history"),
        
    path("chat/delete/<int:room_id>/", DeleteChatRoomView.as_view(), name="delete-room"),

    # DELETE http://127.0.0.1:8000/chat/delete/1/?user_id=5

]