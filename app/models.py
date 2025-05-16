import os, magic
from django.db import models
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from functools import partial
from .keys import KEY_CHOICES
from django.core.validators import MaxValueValidator, MinValueValidator

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError('Image format not supported. Use .jpg, .jpeg, or .png')

def validate_coverimage_size(value):
    max_size = 2 * 1024 * 1024  # 2 MB
    if value.size > max_size:
        raise ValidationError('The cover image cannot exceed 2MB.')

class UploadableItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(
        validators=[validate_image_extension, validate_coverimage_size]
    )
    tags = models.ManyToManyField(Tag, related_name='items_%(class)s', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='likes_%(class)s', blank=True)
    class Meta:
        abstract = True

    def likes_count(self):
        return self.likes.count()
    
    def comments_count(self):
        content_type = ContentType.objects.get_for_model(self)
        return Comment.objects.filter(content_type=content_type, object_id=self.id).count()
    
def validate_audio_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ['.wav', '.mp3', '.flac']:
        raise ValidationError('Audio format not supported. Use .wav, .mp3, or .flac')


def validate_fileMB_size(value,size_MB=10):
    max_size = size_MB * 1024 * 1024 
    if value.size > max_size:
        raise ValidationError('The audio file cannot exceed 10MB.')

validate_fileMB_size_20 = partial(validate_fileMB_size, size_MB=20)
validate_fileMB_size_10 = partial(validate_fileMB_size, size_MB=10)


def user_directory_path(instance, filename, subfolder):
    return f'users/{instance.user.id}/{subfolder}/{filename}'

def loop_audio_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'loops/audio')

def loop_cover_upload_path(instance, filename):
    return user_directory_path(instance, filename, 'loops/covers')

class Loop(UploadableItem):
    audio_file = models.FileField(
        upload_to=loop_audio_upload_path,
        validators=[validate_audio_extension, validate_fileMB_size_10]
    )
    key = models.CharField(max_length=10, choices=KEY_CHOICES, blank=True, null=True)
    bpm = models.PositiveIntegerField(
            blank=True,
            null=True,
            validators=[
                MinValueValidator(0),
                MaxValueValidator(999)
            ]
        )
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    time_signature_num = models.PositiveIntegerField(blank=True, null=True, default=4)
    time_signature_den = models.PositiveIntegerField(blank=True, null=True, default=4)

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

class SamplePack(UploadableItem):
    zip_file = models.FileField(
        upload_to=samplepack_zip_upload_path,
        validators=[validate_zip_extension, validate_fileMB_size_20]
    )
    preview_audio = models.FileField(
        upload_to=samplepack_preview_upload_path,
        validators=[validate_audio_extension, validate_fileMB_size_10],
        blank=True, null=True
    )

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
        
@receiver(pre_delete, sender=Loop)
def delete_loop_files(sender, instance, **kwargs):
    """Elimina i file quando il modello viene cancellato"""
    if instance.audio_file:
        instance.audio_file.delete(save=False)
    if instance.cover_image:
        instance.cover_image.delete(save=False)
        
@receiver(pre_delete, sender=SamplePack)
def delete_samplepack_files(sender, instance, **kwargs):
    """Elimina i file quando il modello SamplePack viene cancellato"""
    if instance.zip_file:
        instance.zip_file.delete(save=False)
    if instance.cover_image:
        instance.cover_image.delete(save=False)
    if instance.preview_audio:
        instance.preview_audio.delete(save=False)

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    upload = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    body = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='likes_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def likes_count(self):
        return self.likes.count()

    def replies_count(self):
        return self.replies.count()    

class Repost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')



