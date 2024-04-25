from django.contrib import admin
from .forms import *
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff']
    # inlines = []


admin.site.register(CustomUser, CustomUserAdmin)