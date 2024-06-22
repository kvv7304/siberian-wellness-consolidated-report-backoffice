from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

class User(AbstractUser):
    sw_numer = models.CharField(max_length=100, default='')
    sw_password = models.CharField(max_length=100, default='')
    sw_name = models.CharField(max_length=100, default='')
    sw_phone = models.CharField(max_length=12, default='')
    sw_email = models.CharField(max_length=12, default='')
    status = models.BooleanField(default=True)
    objects = UserManager()