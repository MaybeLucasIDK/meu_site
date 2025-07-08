import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_uuid = self.scope['url_route']['kwargs']['room_uuid']
        self.room_group_name = f'chat_{self.room_uuid}'

        @database_sync_to_async
        def room_exists(uuid):
            from .models import ChatRoom
            return ChatRoom.objects.filter(id=uuid).exists()

        if not await room_exists(self.room_uuid):
            await self.close()
            return

        # Entra no grupo da sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Sai do grupo da sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recebe mensagem do WebSocket (do cliente)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        is_from_admin = data.get('is_from_admin', False)
        
        # Salva a mensagem no banco
        try:
          await self.save_message(message, is_from_admin)
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': f'failed to save message: {str(e)}'
            }))

        # Envia a mensagem para o grupo da sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'is_from_admin': is_from_admin
            }
        )

    # Recebe a mensagem do grupo da sala e envia para o cliente
    async def chat_message(self, event):
        message = event['message']
        is_from_admin = event['is_from_admin']

        # Envia mensagem para o WebSocket (para o browser)
        await self.send(text_data=json.dumps({
            'message': message,
            'is_from_admin': is_from_admin
        }))

    @database_sync_to_async
    def save_message(self, message, is_from_admin):
        from .models import ChatRoom, ChatMessage

        room = ChatRoom.objects.get(id=self.room_uuid)
        author = self.scope['user'] if is_from_admin and self.scope['user'].is_authenticated else None
        
        ChatMessage.objects.create(
            room=room,
            message=message,
            is_from_admin=is_from_admin,
            author=author
        )