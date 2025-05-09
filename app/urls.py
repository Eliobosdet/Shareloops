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
    path('detail/loop/<int:pk>/', views.LoopDetailView.as_view(), name='loop_detail'),
    path('detail/samplepack/<int:pk>/', views.SamplePackDetailView.as_view(), name='samplepack_detail'),
    path('upload/', views.upload, name='upload'),
    path('upload/loop', views.upload_loop, name='uploadloop'),
    path('upload/samplepack', views.upload_samplepack, name='uploadsamplepack'),
    path('loops/', views.LoopsListView.as_view(), name='loops_list'),
    path('samplepacks/', views.SamplePacksListView.as_view(), name='samplepacks_list'),
    path('like/<int:pk>/<str:modeltype>/', views.like_upload, name='like_upload'),
    path('delete/load/<int:pk>/<str:modeltype>/', views.delete_upload_view, name='delete_upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
