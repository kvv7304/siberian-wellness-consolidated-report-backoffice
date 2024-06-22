# from django.contrib import admin
# from .models import User
# admin.site.register(User)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'sw_name', 'sw_phone', 'sw_email','sw_numer', 'date_joined')

admin.site.register(User, CustomUserAdmin)