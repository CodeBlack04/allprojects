from django.db import models

from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone

import uuid

# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, email, name, password, **extra_fields):
        if not email:
            return ValueError('Please provide a valid email address!')
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email=None, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, password, **extra_fields)

    def create_superuser(self, email=None, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, name, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    CUSTOMER = 'customer'
    AGENT = 'agent'
    MANAGER = 'manager'

    ROLE_CHOICES = (
        (CUSTOMER, 'Customer'),
        (AGENT, 'Agent'),
        (MANAGER, 'Manager'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]
