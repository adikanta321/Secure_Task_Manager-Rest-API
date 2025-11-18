# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.urls import reverse
from .forms import *
from django.utils import timezone
from .models import PasswordResetOTP
from .utils import create_and_send_otp, authenticate_by_email_or_username
from django.contrib.auth.decorators import login_required
import base64
import uuid
from django.core.files.base import ContentFile
@login_required
def profile_view(request):
    return render(request, 'profile.html', {})


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        # If the JS sent a base64 cropped image, it will be in POST['cropped_image']
        cropped_b64 = request.POST.get('cropped_image', '')
        use_fallback = request.POST.get('use_fallback', '0')  # '1' if using direct file input

        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # If there is cropped image string, decode and save it
            if cropped_b64:
                # cropped_b64 looks like: data:image/png;base64,AAAA...
                if ',' in cropped_b64:
                    header, b64data = cropped_b64.split(',', 1)
                else:
                    b64data = cropped_b64
                try:
                    decoded_file = base64.b64decode(b64data)
                except (TypeError, ValueError):
                    messages.error(request, "Could not decode the cropped image.")
                    return render(request, 'accounts/edit_profile.html', {'form': form})

                # Create file name and ContentFile
                file_name = f'avatar_{uuid.uuid4().hex[:12]}.png'
                form.instance.profile_image.save(file_name, ContentFile(decoded_file), save=False)

            # If user didn't use crop and uploaded a file, Django handles request.FILES as usual.
            # Save the form (which saves profile_image if uploaded)
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=user)

    return render(request, 'edit_profile.html', {'form': form})
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # change to your home/dashboard url name

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.get_short_name() or user.username or user.email}!")
            # redirect to next if present
            next_url = request.GET.get('next') or reverse('home')
            return redirect(next_url)
        else:
            # form __clean__ will add error messages to the form itself
            messages.error(request, "Login failed. Please fix the errors below.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please login.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def request_otp_view(request):
    """
    Step 1: user provides email => we send OTP to that email.
    """
    if request.method == 'POST':
        form = RequestOTPForm(request.POST)
        if form.is_valid():
            user = form.user
            # Optionally, we can throttle OTP creation per user here
            create_and_send_otp(user)
            messages.success(request, "OTP sent to your email. Check inbox and spam (10 min expiry).")
            return redirect(reverse('accounts:verify_otp') + f"?email={user.email}")
        else:
            messages.error(request, "Please correct the error.")
    else:
        form = RequestOTPForm()
    return render(request, 'request_otp.html', {'form': form})

def verify_otp_view(request):
    """
    Step 2: user submits email + otp + new password
    """
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower()
            otp_code = form.cleaned_data['otp'].strip()

            # Safely get the user model instance
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "No account found for that email.")
                return render(request, 'accounts/verify_otp.html', {'form': form})

            # get latest unused OTP for this user matching code
            try:
                otp = PasswordResetOTP.objects.filter(
                    user=user, code=otp_code, used=False
                ).latest('created_at')
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, "Invalid OTP. Please check the code and try again.")
                return render(request, 'verify_otp.html', {'form': form})

            if otp.is_expired:
                messages.error(request, "OTP has expired. Request a new one.")
                return render(request, 'verify_otp.html', {'form': form})

            # all good — set password
            new_password = form.cleaned_data['password1']
            user.set_password(new_password)
            user.save()
            otp.mark_used()
            messages.success(request, "Password reset successful. You can now login.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # allow pre-filling email from query param
        initial = {}
        email_q = request.GET.get('email')
        if email_q:
            initial['email'] = email_q
        form = VerifyOTPForm(initial=initial)
    return render(request, 'verify_otp.html', {'form': form})