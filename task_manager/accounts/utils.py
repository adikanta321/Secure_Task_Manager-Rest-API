from django.contrib.auth import get_user_model, authenticate
import random
from django.core.mail import send_mail
from .models import *
from django.conf import settings

User = get_user_model()


# Simple function to authenticate either by email or username

def authenticate_by_email_or_username(request,identifier, password):
    # First try to authenticate by email (django authenticate will use AUTHENTICATION_BACKENDS)
    user = authenticate(request, username =identifier, password=password)
    if user: 
        return user
    # if the identifier looks like an email but authenticate failed, try to fetch user by username
    try:
        # if identifier is email stored as email field, django `authenticate` above works because USERNAME_FIELD=email
        # but for username login we try to find user with username matching identifier
        user_obj = User.objects.get(username=identifier).first()
        if user_obj and user_obj.check_password(password):
            return user_obj
    except User.DoesNotExist:
        return None
    return None

def generate_otp_code():
    return f"{random.randint(0, 999999):06d}"  # zero-padded 6 digits

def create_and_send_otp(user):
    # create OTP record
    code = generate_otp_code()
    otp = PasswordResetOTP.objects.create(user=user, code=code)
    # send email
    subject = "Your OTP for Secure Task Manager password reset"
    message = f"Hello {user.get_short_name() or user.username},\n\nYour password reset OTP is: {code}\nIt expires in 10 minutes.\n\nIf you didn't request this, ignore this email.\n\n— Secure Task Manager"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    return otp