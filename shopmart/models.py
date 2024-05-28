from django.db import models
from core.models import User

from datetime import timedelta
from django.utils import timezone

import uuid
# Create your models here.
from django.db import models

# Create your models here.
class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.full_name}--{self.subject}--{self.message}'













class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=191)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    
class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=191)
    price = models.FloatField()

    created_by = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    
    description = models.TextField( blank=True, null=True )
    image = models.ImageField(upload_to='shopmart/product_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_sold = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(null=True, blank=True)
    reservation_duration = timedelta(minutes=1)
    reserved_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    def reserve(self, user):
        self.is_reserved = True
        self.reserved_by = user
        self.reserved_at = timezone.now()
        self.save()

    def unreserve(self):
        self.is_reserved = False
        self.reserved_by = None
        self.reserved_at = None
        self.save()

    def is_reservation_expired(self):
        if self.is_reserved:
            if timezone.now() > self.reserved_at + self.reservation_duration:
                return True
            else:
                return False
        else:
            return True

    def __str__(self):
        return f'{self.name}--{self.created_by.name}'















class ConversationMessage(models.Model):
    body = models.TextField()
    sent_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.sent_by}-{self.body}'
    
    class Meta:
        ordering = ('created_at',)

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    product = models.ForeignKey(Product, related_name='chatrooms', blank=True, null=True, on_delete=models.CASCADE)
    messages = models.ManyToManyField(ConversationMessage, blank=True)
    members = models.ManyToManyField(User, related_name='chatrooms')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.product.name}-{self.id}'
    
    class Meta:
        ordering = ('-created_at',)