from django.urls import path
from .views import CreateChatRoomView, ChatHistoryView, ChatRoomListView, BulkDeleteChatRoomView

urlpatterns = [
    path("chat/create-room/", CreateChatRoomView.as_view(), name="create-room"),

    path("chat/rooms/<int:user_id>/", ChatRoomListView.as_view(), name="chat-rooms"),

    path("chat/history/<int:room_id>/", ChatHistoryView.as_view(), name="chat-history"),
        
    path("chat/delete-bulk/", BulkDeleteChatRoomView.as_view(), name="delete-bulk-room"),


]