from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
import logging
# from django.contrib.auth.forms import AuthenticationForm

logger = logging.getLogger(__name__)

def home(request, *args, **kwargs):
    tmp_name="home.html"
    return render(request,tmp_name)

def register_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                logger.info(f"User {user.username} logged in successfully.")  # Log di debug
                login(request, user)
                return redirect('home')
            else:
                logger.warning("Form valid but user is None.")
        else:
            logger.warning(f"Login form invalid: {form.errors}")
    else:
        form = CustomLoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('home')

def profile_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return render(request, 'user/profile.html', {'user': request.user})
    else:
        return redirect('login')

class ProfileDetailView(DetailView):
    model = User
    template_name = 'user/profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loops'] = self.object.loops.all()
        context['profImg'] = getattr(self.object, 'profileimage', None)
        context['profForm'] = ProfileImageUpdateForm()
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj
    
    def post(self, request, *args, **kwargs):
            self.object = self.get_object()  # Ottieni l'utente corrente
            profile_image = getattr(self.object, 'profileimage', None)  # Ottieni l'istanza di ProfileImage

            if profile_image is None:
                # Se non esiste un'istanza di ProfileImage, creane una
                profile_image = ProfileImage.objects.create(user=self.object)

            form = ProfileImageUpdateForm(request.POST, request.FILES, instance=profile_image)

            if form.is_valid():
                old_image = None
                if profile_image.image.name != 'defaultProfileImage.jpg':
                    old_image = profile_image.image

                form.save()

                if old_image:
                    old_image.delete(save=False)

                messages.success(request, "Immagine del profilo aggiornata con successo!")
                return redirect('profile', pk=self.object.id)
            else:
                print(form.errors)
            # Se il form non è valido, ricarica la pagina con gli errori
            context = self.get_context_data()
            context['profForm'] = form
            return self.render_to_response(context)    
# class ProfileUpdateView(UpdateView):
#     model = User
#     template_name = 'user/profile_edit.html'
#     form_class = CustomRegisterForm

#     def get_object(self, queryset=None):
#         return self.request.user

#     def form_valid(self, form):
#         user = form.save(commit=False)
#         user.save()
#         messages.success(self.request, 'Profile updated successfully!')
#         return redirect('profile', pk=user.id)
    

@login_required
@require_POST
def remove_profile_image(request, pk=None):
    profile = request.user.profileimage
    profile.image.delete(save=False)  # elimina il file fisico
    profile.image = 'defaultProfileImage.jpg'  # imposta l'immagine predefinita
    profile.save()
    return redirect('profile', pk=pk)

   
class LoopsListView(ListView):
    model = Loop
    template_name = 'loops.html'
    context_object_name = 'loops'



@login_required
def upload_loop(request):
    if request.method == 'POST':
        form = LoopForm(request.POST, request.FILES)
        if form.is_valid():
            loop = form.save(commit=False)
            loop.user = request.user
            loop.save()
            messages.success(request, 'Loop uploaded successfully!')
            return redirect('home')
    else:
        form = LoopForm()
    return render(request, 'user/upload_loop.html', {'form': form})