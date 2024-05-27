from django.contrib import admin

from .models import Amenity, Hotel, HotelRoom, HotelImage, HotelRoomImage, Booking, Rating, Room, Message

# Register your models here.

admin.site.register(Amenity)

admin.site.register(Hotel)
admin.site.register(HotelImage)

admin.site.register(HotelRoom)
admin.site.register(HotelRoomImage)

admin.site.register(Booking)
admin.site.register(Rating)

admin.site.register(Room)
admin.site.register(Message)