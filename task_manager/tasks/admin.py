# tasks/admin.py
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'is_favorite', 'created_at')
    list_filter = ('status', 'is_favorite')
    search_fields = ('title', 'description', 'owner__username', 'owner__email')
