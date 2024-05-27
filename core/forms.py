from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import User


INPUT_CLASSES = 'w-full mb-4 py-4 px-6 rounded-xl text-gray-800 border'

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email','name')
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Your email-address...',
                'class': INPUT_CLASSES,
            }),

            'name': forms.TextInput(attrs={
                'placeholder': 'Your name...',
                'class': INPUT_CLASSES,
            }),
        }

    password1 = forms.CharField(label='Create a password:', widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password...',
        'class': INPUT_CLASSES
    }))

    password2 = forms.CharField(label='Repeat password:', widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat your password...',
        'class': INPUT_CLASSES
    }))

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Enter your email address: ', widget=forms.EmailInput(attrs={
        'placeholder': 'example@example.com',
        'class': INPUT_CLASSES
    }))

    password = forms.CharField(label='Enter your password: ', widget=forms.PasswordInput(attrs={
        'placeholder': 'Password...',
        'class': INPUT_CLASSES
    }))


class MyPasswordResetForm(PasswordResetForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': INPUT_CLASSES
    }))

class MySetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={
        'placeholder': 'New password',
        'class': INPUT_CLASSES
    }))

    new_password2 = forms.CharField(label='Repeat new password', widget=forms.PasswordInput(attrs={
        'placeholder': 'New password confirmation',
        'class': INPUT_CLASSES
    }))