from django.db import models
from django.contrib.auth import get_user_model

# Chatbot
class Conversation(models.Model):
    conversation_id = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.conversation_id

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
    
