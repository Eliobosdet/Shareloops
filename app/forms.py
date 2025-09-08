from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from .keys import KEY_CHOICES
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


class ProfileUpdateForm(forms.ModelForm):  # Rinominato da ProfileImageUpdateForm
    class Meta:
        model = UserProfile  # o ProfileImage se non hai rinominato
        fields = ['image', 'bio', 'instagram', 'youtube', 'soundcloud']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Racconta qualcosa di te...'
            }),
            'instagram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'username (senza @)'
            }),
            'youtube': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/channel/...'
            }),
            'soundcloud': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://soundcloud.com/username'
            }),
        }
class LoopForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width:100%;'}),
        required=False,
        label="Tags",
        help_text="Select one or more"
    )

    class Meta:
        model = Loop
        fields = [
            'title', 'description', 'audio_file', 'bpm', 'key',
            'time_signature_num', 'time_signature_den', 'genre', 'cover_image'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()
    
class SamplePackForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width:100%;'}),
        required=False,
        label="Tags",
        help_text="Select one or more"
    )
    
    class Meta:
        model = SamplePack
        fields = ['title', 'description', 'zip_file', 'cover_image', 'preview_audio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write a comment...', 
                'rows': 1  # Set the maximum number of rows
            }),
        }

class SearchForm(forms.Form):
    title = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search for artists, bands, loops and samplepacks'}),
    )

class FilterForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2', 'style': 'width:100%;'}),
        required=False,
        label="Tags",
        help_text="Select one or more"
    )
    key = forms.ChoiceField(
        choices=[('', 'All')] + KEY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    bpm_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM Min'})
    )
    bpm_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM Max'})
    )
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    upload_type = forms.ChoiceField(
        choices=[('', 'All'), ('loop', 'Loop'), ('samplepack', 'Sample Pack')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
