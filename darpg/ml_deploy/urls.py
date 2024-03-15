from django.urls import path
from .views import ConversationView, MessageView

urlpatterns = [
    path('start-chat/', ConversationView.as_view(), name='start-chat'),
    path('send-msg/<std:conversation_id>/', MessageView.as_view(), name='send-message')
]