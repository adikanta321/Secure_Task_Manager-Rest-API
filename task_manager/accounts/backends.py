# accounts/backends.py
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate using either email or username.
    Falls back to ModelBackend behaviour for username lookups.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # The Django auth system calls this with username kwarg from the form.
        # We'll try to locate a user by email first, then by username.
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        # try email lookup
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            # try username lookup (case-sensitive as Django default)
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
