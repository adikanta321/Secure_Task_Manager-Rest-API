# tasks/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner_email = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'owner', 'owner_username', 'owner_email',
            'title', 'description', 'status', 'is_favorite',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('owner', 'created_at', 'updated_at')
