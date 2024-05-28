from django.urls import path
from bookmyhotel import consumers as bmhconsumers
from shopmart import consumers as smconsumers

websocket_urlpatterns = [
    path('ws/bookmyhotel/<str:room_id>/', bmhconsumers.ChatConsumer.as_asgi()),
    path('ws/shopmart/<str:room_id>/', smconsumers.ChatConsumer.as_asgi()),
]