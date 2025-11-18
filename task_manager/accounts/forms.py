# accounts/forms.py
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_image']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'profile_image': forms.FileInput(attrs={'class':'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        user = self.instance
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise ValidationError("Email already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        user = self.instance
        if username and User.objects.filter(username=username).exclude(pk=user.pk).exists():
            raise ValidationError("Username already taken.")
        return username




class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={'placeholder': 'Email or username', 'class': 'form-control'}),
        max_length=254
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get('username_or_email')
        password = cleaned.get('password')

        if identifier and password:
            user = authenticate(username=identifier, password=password)
            if user is None:
                raise forms.ValidationError("Invalid credentials. Please check email/username and password.")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")
            self.user = user
        return cleaned

    def get_user(self):
        return self.user

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        super_clean = super().clean()
        p1 = super_clean.get('password1')
        p2 = super_clean.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return super_clean

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class RequestOTPForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError("No account found with this email.")
        self.user = user
        return email


class VerifyOTPForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'6-digit code'}))
    password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return cleaned