from django.contrib import admin
from .models import Loop, SamplePack, UserProfile, Comment, Genre, Tag

admin.site.register(Loop)
admin.site.register(SamplePack)
admin.site.register(UserProfile)
admin.site.register(Comment)
admin.site.register(Genre)
admin.site.register(Tag)