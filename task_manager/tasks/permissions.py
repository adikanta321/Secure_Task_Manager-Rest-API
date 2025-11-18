# tasks/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow only owners to edit/delete. Authenticated users may read.
    """

    def has_permission(self, request, view):
        # require authentication for any access (you can make list/create allowed for authenticated only)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # SAFE methods allowed (GET, HEAD, OPTIONS) for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
