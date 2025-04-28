from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Row, Column, Submit

class CustomRegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        min_length=2,
        required=True,
        label="Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        min_length=2,
        required=True,
        label="Surname",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        max_length=254,
        min_length=5,
        label="Email",
        help_text="Required. Inform a valid email address.",
        error_messages={'required': 'Email is required'},
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=150,
        min_length=2,
        required=True,
        label="Username",
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        error_messages={'required': 'Username is required'},
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        max_length=32,
        min_length=8,
        required=True,
        help_text="Required. 8 characters or more. Letters, digits and @/./+/-/_ only.",
        error_messages={'required': 'Password is required'},
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        max_length=32,
        min_length=8,
        required=True,
        help_text="Repeat password for verification.",
        error_messages={'required': 'Password confirmation is required'},
        label="Repeat Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']