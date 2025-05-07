import os, magic
from django.db import models
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from functools import partial



def validate_audio_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac']:
        raise ValidationError('Audio format not supported. Use .wav, .mp3, or .flac')

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError('Image format not supported. Use .jpg, .jpeg, or .png')

def validate_fileMB_size(value,size_MB=10):
    max_size = size_MB * 1024 * 1024 
    if value.size > max_size:
        raise ValidationError('The audio file cannot exceed 10MB.')

validate_fileMB_size_20 = partial(validate_fileMB_size, size_MB=20)
validate_fileMB_size_10 = partial(validate_fileMB_size, size_MB=10)

def validate_coverimage_size(value):
    max_size = 2 * 1024 * 1024  # 2 MB
    if value.size > max_size:
        raise ValidationError('The cover image cannot exceed 2MB.')

def user_directory_path(instance, filename, subfolder):
    return f'users/{instance.user.id}/{subfolder}/{filename}'

def loop_audio_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'loops/audio')

def loop_cover_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'loops/covers')

class Loop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loops')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    audio_file = models.FileField(
        upload_to=loop_audio_upload_path,
        validators=[validate_audio_extension, validate_fileMB_size_10]
    )
    cover_image = models.ImageField(
        upload_to=loop_cover_upload_path,
        validators=[validate_image_extension, validate_coverimage_size]
    )
    key = models.CharField(max_length=10, blank=True, null=True, help_text="Example: C, Dm")
    bpm = models.PositiveIntegerField(blank=True, null=True, help_text="Example: 120, 140")
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Separate tags with commas")
    genre = models.CharField(max_length=100, blank=True, null=True)
    time_signature = models.CharField(max_length=10, blank=True, null=True, help_text="Example: 4/4, 3/4")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"

def validate_zip_extension(file):
    if not file.name.endswith('.zip'):
        raise ValidationError("Il file deve avere estensione .zip.")
    # Controllo MIME type reale (non solo estensione)
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Torna all’inizio per evitare problemi in seguito
    if mime != 'application/zip':
        raise ValidationError("Il file caricato non è un file ZIP valido.")
    
def samplepack_zip_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'samplepacks/zips')

def samplepack_cover_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'samplepacks/image_covers')

def samplepack_preview_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'samplepacks/preview')

class SamplePack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='samplepacks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    zip_file = models.FileField(
        upload_to=samplepack_zip_upload_path,
        validators=[validate_zip_extension, validate_fileMB_size_20]
    )
    cover_image = models.ImageField(
        upload_to=samplepack_cover_upload_path,
        validators=[validate_image_extension, validate_coverimage_size]
    )
    preview_audio = models.FileField(
        upload_to=samplepack_preview_upload_path,
        validators=[validate_audio_extension, validate_fileMB_size_10],
        blank=True, null=True, default=None
    )
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Separate tags with commas")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.user.username}"

def profileimage_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'profile_image')

class ProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=profileimage_upload_path, 
        validators=[validate_image_extension, validate_coverimage_size],
        default='defaultProfileImage.jpg',
        max_length=255
    )
    
    def save(self, *args, **kwargs):
        # Sovrascrivi il salvataggio per rinominare il file
        if self.image and self.image.name != 'defaultProfileImage.jpg':
            # Ottieni l'estensione del file originale
            ext = os.path.splitext(self.image.name)[1]
            # Imposta il nuovo nome
            self.image.name = f'img{ext}'  # Es: img.jpg, img.png
        super().save(*args, **kwargs)
        
@receiver(post_save, sender=User)
def create_profile_image(sender, instance, created, **kwargs):
    if created:
        try:
            ProfileImage.objects.create(user=instance)
        except Exception as e:
            print(f"Errore nella creazione dell'immagine profilo: {e}")
