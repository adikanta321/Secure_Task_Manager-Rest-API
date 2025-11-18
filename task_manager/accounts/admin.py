# accounts/admin.py
from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('username', 'first_name', 'last_name', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
