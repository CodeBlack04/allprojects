from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from django.utils.timesince import timesince

from .models import Room, Message
from core.models import User

from .templatetags.chatextras import initials

import json


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        #join room group
        await self.get_room()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        #inform client about joining chat
        if self.user.is_staff:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'inform_client'
                }
            )


    async def disconnect(self, close_code):
        #Leave room
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if not self.user.is_staff:
            await self.set_room_closed()


    async def receive(self, text_data):
        #Receive message from websocket(frontend)
        text_data_json = json.loads(text_data)

        type = text_data_json['type']
        message = text_data_json.get('message', '')
        name = text_data_json.get('name', '')
        client = text_data_json.get('client', '')
        agent = text_data_json.get('agent', '')

        print('Receive:', type)

        if type == 'message':
            new_message = await self.create_message(message, client, agent)

            # send message to group/ room
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'chat_message',
                'message': message,
                'name': name,
                'initials': initials(name),
                'client': client,
                'agent': agent,
                'created_at': timesince(new_message.created_at),
            })
        elif type == 'writing_on':
            # send message to group/ room
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'add_writing_status',
                'message': message,
                'name': name,
                'initials': initials(name),
                'client': client,
                'agent': agent,
            })
        elif type == 'writing_off':
            # send message to group/ room
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'remove_writing_status',
            })


    async def chat_message(self, event):
        # Send message to WebSocket (front end)
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'name': event['name'],
            'initials': event['initials'],
            'client': event['client'],
            'agent': event['agent'],
            'created_at': event['created_at'],
        }))

    
    async def inform_client(self, event):
        # Send message to WebSocket (front end)
        await self.send(text_data=json.dumps({
            'type': 'inform_client'
        }))


    async def add_writing_status(self, event):
        # Send message to WebSocket (front end)
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'name': event['name'],
            'initials': event['initials'],
            'client': event['client'],
            'agent': event['agent'],
        }))


    async def remove_writing_status(self, event):
        # Send message to WebSocket (front end)
        await self.send(text_data=json.dumps({
            'type': event['type']
        }))



    @sync_to_async
    def get_room(self):
        self.room = Room.objects.get(room_id=self.room_name)

    @sync_to_async
    def set_room_closed(self):
        self.room = Room.objects.get(room_id=self.room_name)
        self.room.status = Room.CLOSED
        self.room.save()

    @sync_to_async
    def create_message(self, message, client, agent):
        message = Message.objects.create(body=message)

        if client:
            message.sent_by = User.objects.get(pk=client)
            message.save()
        else :
            message.sent_by = User.objects.get(pk=agent)
            message.save()

        self.room.messages.add(message)

        return message