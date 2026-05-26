from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CreateConversationSerializer

User = get_user_model()


class ConversationListCreateView(APIView):
    def get(self, request):
        convos = Conversation.objects.filter(participants=request.user).prefetch_related("participants", "messages")
        serializer = ConversationSerializer(convos, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateConversationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participant_id = serializer.validated_data["participant_id"]
        other_user = get_object_or_404(User, pk=participant_id)

        # Check if conversation already exists between these two users
        existing = Conversation.objects.filter(participants=request.user).filter(participants=other_user)

        if existing.exists():
            convo = existing.first()
            return Response(ConversationSerializer(convo, context={"request": request}).data)

        convo = Conversation.objects.create()
        convo.participants.add(request.user, other_user)
        return Response(
            ConversationSerializer(convo, context={"request": request}).data, status=status.HTTP_201_CREATED
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        convo = get_object_or_404(Conversation, pk=self.kwargs["pk"], participants=self.request.user)
        # Mark messages from other users as read
        convo.messages.exclude(sender=self.request.user).filter(is_read=False).update(is_read=True)
        return convo.messages.select_related("sender__profile").all()


class SendMessageView(APIView):
    def post(self, request, pk):
        convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
        content = request.data.get("content", "").strip()
        if not content:
            return Response({"error": "Message content is required"}, status=400)
        msg = Message.objects.create(conversation=convo, sender=request.user, content=content)
        convo.save()  # bump updated_at
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)


class MarkReadView(APIView):
    def put(self, request, pk):
        convo = get_object_or_404(Conversation, pk=pk, participants=request.user)
        updated = convo.messages.exclude(sender=request.user).filter(is_read=False).update(is_read=True)
        return Response({"marked_read": updated})
