# accounts/models.py
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils import timezone
from datetime import timedelta
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        if not username:
            # generate a fall-back username from email local-part
            username = email.split('@')[0]
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        # ensure username exists
        if not username:
            username = email.split('@')[0]

        return self.create_user(email, username=username, password=password, **extra_fields)


def user_profile_path(instance, filename):
    return f'profiles/user_{instance.id}/{filename}'


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to=user_profile_path, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Avoid reverse accessor name clashes (safe approach during development)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='+',
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='+',
        blank=True,
        help_text='Specific permissions for this user.'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'   # login identifier
    REQUIRED_FIELDS = ['username']  # username required when creating superuser via createsuperuser

    def __str__(self):
        return self.username or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        return self.first_name or self.username or self.email

class PasswordResetOTP(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='password_otps')
    code = models.CharField(max_length=6)  # store as string, e.g. "123456"
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    # expires after N minutes (we'll check this in logic)
    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)  # 10 minutes expiry

    def mark_used(self):
        self.used = True
        self.save()