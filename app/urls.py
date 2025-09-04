"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^(home/)?$', views.home, name='home'),  
    path('login/', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/<int:pk>/removeprofileimage/', views.remove_profile_image, name='rm_profile_img'),
    path('profile/<int:pk>/change_password/', views.change_password, name='change_password'),
    path('detail/<str:modeltype>/<int:pk>/', views.GenericDetailView.as_view(), name='uploadable_detail'),
    path('upload/', views.upload, name='upload'),
    path('upload/loop', views.upload_loop, name='uploadloop'),
    path('upload/samplepack', views.upload_samplepack, name='uploadsamplepack'),
    path('edit/<str:modeltype>/<int:pk>/', views.edit_uploadable, name='edit_uploadable'),
    path('loops/', views.LoopsListView.as_view(), name='loops_list'),
    path('samplepacks/', views.SamplePacksListView.as_view(), name='samplepacks_list'),
    path('like/<int:pk>/<str:modeltype>/', views.like_uploadable, name='like_uploadable'),
    path('delete/load/<int:pk>/<str:modeltype>/', views.delete_uploadable, name='delete_uploadable'),
    path('add/comment/<int:pk>/<str:modeltype>/', views.add_comment, name='add_comment'),
    path('add/comment/<int:pk>/<str:modeltype>/<int:parent_id>/', views.add_comment, name='add_comment_with_parent'),    
    path('like/<int:pk>/comment/', views.like_comment, name='like_comment'),
    path('delete/comment/<int:pk>/<str:modtype>/<int:upl_pk>', views.delete_comment, name='delete_comment'),
    path('<str:modeltype>/<int:pk>/download/', views.audio_file_download, name='audio_file_download'),
    path('<str:modeltype>/<int:pk>/track_play/', views.track_audio_play, name='track_audio_play'),
    # path('loop/<int:loop_id>/track_download/', views.track_audio_download, name='track_audio_download')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
