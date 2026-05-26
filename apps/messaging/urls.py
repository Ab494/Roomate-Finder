from django.urls import path
from .views import ConversationListCreateView, MessageListView, SendMessageView, MarkReadView

urlpatterns = [
    path("", ConversationListCreateView.as_view(), name="conversation-list"),
    path("<int:pk>/messages/", MessageListView.as_view(), name="message-list"),
    path("<int:pk>/messages/send/", SendMessageView.as_view(), name="message-send"),
    path("<int:pk>/messages/read/", MarkReadView.as_view(), name="message-read"),
]
