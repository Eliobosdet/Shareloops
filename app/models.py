from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

def validate_audio_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac']:
        raise ValidationError('Audio format not supported. Use .wav, .mp3, or .flac')

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError('Image format not supported. Use .jpg, .jpeg, or .png')

def validate_file_size(value):
    max_size = 10 * 1024 * 1024  # 10 MB
    if value.size > max_size:
        raise ValidationError('The audio file cannot exceed 10MB.')

def validate_cover_size(value):
    max_size = 2 * 1024 * 1024  # 2 MB
    if value.size > max_size:
        raise ValidationError('The cover image cannot exceed 2MB.')

class Loop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loops')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    audio_file = models.FileField(
        upload_to='loops/',
        validators=[validate_audio_extension, validate_file_size]
    )
    tags = models.CharField(max_length=255, help_text="Separate tags with commas")
    bpm = models.PositiveIntegerField(blank=True, null=True, help_text="Example: 120, 140")
    key = models.CharField(max_length=10, blank=True, null=True, help_text="Example: C, Dm")
    time_signature = models.CharField(max_length=10, blank=True, null=True, help_text="Example: 4/4, 3/4")
    genre = models.CharField(max_length=100)
    cover_image = models.ImageField(
        upload_to='loop_covers/',
        validators=[validate_image_extension, validate_cover_size]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"
