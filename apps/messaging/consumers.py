import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.room_group_name = f"chat_{self.conversation_id}"
        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        # Verify user is participant
        is_participant = await self._is_participant(user, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        content = data.get("content", "").strip()
        if not content:
            return

        user = self.scope["user"]
        message = await self._save_message(user, self.conversation_id, content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message_id": message["id"],
                "content": content,
                "sender_id": user.pk,
                "sender_name": message["sender_name"],
                "created_at": message["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "id": event["message_id"],
                    "content": event["content"],
                    "sender_id": event["sender_id"],
                    "sender_name": event["sender_name"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def _is_participant(self, user, conversation_id):
        from .models import Conversation

        return Conversation.objects.filter(pk=conversation_id, participants=user).exists()

    @database_sync_to_async
    def _save_message(self, user, conversation_id, content):
        from .models import Conversation, Message

        conversation = Conversation.objects.get(pk=conversation_id)
        msg = Message.objects.create(conversation=conversation, sender=user, content=content)
        conversation.save()  # bump updated_at
        return {
            "id": msg.pk,
            "sender_name": user.profile.full_name if hasattr(user, "profile") else user.email,
            "created_at": msg.created_at.isoformat(),
        }
