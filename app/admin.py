from django.contrib import admin
from .models import Loop, SamplePack, ProfileImage, Comment, Genre

admin.site.register(Loop)
admin.site.register(SamplePack)
admin.site.register(ProfileImage)
admin.site.register(Comment)
admin.site.register(Genre)