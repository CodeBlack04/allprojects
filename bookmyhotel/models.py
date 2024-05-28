from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import User

import uuid

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LocationType(models.TextChoices):
    URBAN = 'UR', 'Urban'
    AIRPORT = 'AP', 'Airport'
    RESORT = 'RE', 'Resort'
    MOUNTAIN = 'MT', 'Mountain'
    BEACHFRONT = 'BF', 'Beachfront'
    BOUTIQUE = 'BO', 'Boutique'
    ECO = 'EC', 'Eco'
    HIGHWAY = 'HW', 'Highway'
    CASINO = 'CA', 'Casino'


class RoomType(models.TextChoices):
    STANDARD = 'ST', 'Standard'
    DELUXE = 'DX', 'Deluxe'
    SUITE = 'SU', 'Suit'
    FAMILY = 'FR', 'Family'


class Amenity(BaseModel):
    amenity_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['created_at',]

    def __str__(self):
        return self.amenity_name
    

# Hotel related models    

class Hotel(BaseModel):
    hotel_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    amenities = models.ManyToManyField(Amenity, blank=True)
    location_type = models.CharField(max_length=2, choices=LocationType.choices, default=LocationType.URBAN,)

    # latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    # longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def get_lowest_room_price(self):
        return self.rooms.order_by('price').first().price if self.rooms.exists() else None
    
    def get_average_rating(self):
        ratings = self.ratings.all()

        if not ratings:
            return None
        
        total = sum(rating.average_rating() for rating in ratings)
        count = ratings.count()

        return round(total / count, 2)

    def __str__(self):
        return self.hotel_name
    
class HotelImage(BaseModel):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bookmyhotel/hotel_images')

    def __str__(self):
        return f"Image for {self.hotel.hotel_name}"
    


# Hotel-room related models    

class HotelRoom(BaseModel):
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_number = models.IntegerField(unique=True)
    room_type = models.CharField(max_length=2, choices=RoomType.choices, default=RoomType.STANDARD)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def is_booked(self, check_date):
        return self.bookings.filter(start_date__lte=check_date, end_date__gte=check_date).exists()
    
    def get_average_rating(self):
        ratings = self.ratings.all()

        if not ratings:
            return None
        
        total = sum(rating.average_rating() for rating in ratings)
        count = ratings.count()

        return round(total / count, 2)

    def __str__(self):
        return f'{self.room_number} at {self.hotel.hotel_name}'
    
class HotelRoomImage(BaseModel):
    hotel_room = models.ForeignKey(HotelRoom, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bookmyhotel/hotel_room_images')

    def __str__(self):
        return f"Image for room {self.hotel_room.room_number} at {self.hotel_room.hotel.hotel_name}"
    

# Booking related models

class Booking(BaseModel):
    room = models.ForeignKey(HotelRoom, related_name='bookings', blank=True, null=True, on_delete=models.SET_NULL)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'Booking for {self.room.room_number} at {self.room.hotel.hotel_name} from {self.start_date} to {self.end_date}'
    

# Rating related models

class Rating(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='ratings', blank=True, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(HotelRoom, related_name='ratings', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='ratings', blank=True, null=True, on_delete=models.SET_NULL)
    cleanliness = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    service = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    location = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    amenities = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    room_quality = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def average_rating(self):
        total = self.cleanliness + self.service + self.location + self.amenities + self.room_quality
        return round(total / 5, 2)
    
    def __str__(self):
        return f'Rating {self.average_rating()} for hotel {self.hotel.hotel_name} by {self.user.name}'
    










class Message(models.Model):
    body = models.TextField()
    sent_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sent_by.name}-{self.body}'
    
    class Meta:
        ordering = ('created_at',)


class Room(models.Model):
    WAITING = 'waiting'
    ACTIVE = 'active'
    CLOSED = 'closed'

    ROOM_STATUS = (
        (WAITING, 'Waiting'),
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
    )

    room_id = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)
    messages = models.ManyToManyField(Message, blank=True)

    client = models.ForeignKey(User, related_name='client_rooms', blank=True, null=True, on_delete=models.SET_NULL)
    agent = models.ForeignKey(User, related_name='agent_rooms', blank=True, null=True, on_delete=models.SET_NULL)

    status = models.CharField(max_length=20, choices=ROOM_STATUS, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.client.name}-{self.room_id}-{self.status}'
    
    class Meta:
        ordering = ('-created_at',)
