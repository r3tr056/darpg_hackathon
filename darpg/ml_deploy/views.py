from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from authentication.decorators import only_authenticated_user
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .chat import ChatService
from .chat.decorators import check_conversation_access

chat_service = ChatService()

class ModelCall(APIView):
    def get(self, request):
        if request.method == 'GET':
            params = request.GET.get('sentence')

class ConversationView(APIView):
    @only_authenticated_user
    def post(request):
        user = request.user
        conversation = Conversation.objects.create()
        user.conversations.add(conversation)
        serializer = ConversationSerializer(conversation)
        if serializer.is_valid():
            chat_service.start_conversation(serializer.data['conversation_id'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class MessageView(APIView):
    @only_authenticated_user
    @check_conversation_access
    def post(request, conversation_id):
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        serializer = MessageSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(conversation=conversation)
            message = serializer.data['content']
            chat_service.add_user_message(conversation_id, message)
            # Generate response
            response = chat_service.get_response(conversation_id, message)
            chat_service.add_ai_message(conversation_id, message)

            response_msg = Message.objects.create(conversation=conversation, content=response, sender='Bot')

            return Response({'sender': 'Bot', 'content': response}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatbotSettingsView(APIView):
    @only_authenticated_user
    def get(request):
        pass
    
    @only_authenticated_user
    def post(request):
        pass

class TopicModellerAPIView(APIView):
    def post(request):
        doc_text = request.json['doc_text']
        text_vectorized = vectorizer.transform([doc_text])
        topic_probablity = lda.transform(text_vectorized)
        predicted_topic = topic_probablity.argmax()
        return predicted_topic
    
    