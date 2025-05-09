from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import *
from .utils import get_ordered_loads
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
        # context['loops'] = self.object.loops.all()
        context['profImg'] = getattr(self.object, 'profileimage', None)
        context['profForm'] = ProfileImageUpdateForm()
        context['loads'] = get_ordered_loads(self.object)
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj
    
    def post(self, request, *args, **kwargs):
        print("Entering ProfileDetailView.post method")
        self.object = self.get_object()
        print(f"Retrieved object: {self.object}")

        # Verifica autorizzazione
        if self.object != request.user:
            print(f"Unauthorized access attempt by user: {request.user}")
            messages.error(request, "Non autorizzato")
            return redirect('profile', pk=request.user.pk)

        profile_image, created = ProfileImage.objects.get_or_create(user=self.object)
        print(f"ProfileImage object: {profile_image}, Created: {created}")
        profile_image.refresh_from_db()
        old_image = profile_image.image 
        print(f"old image: {old_image.path}")
        form = ProfileImageUpdateForm(request.POST, request.FILES, instance=profile_image)
        print(f"Form initialized: {form}")

        if form.is_valid():
            print("Form is valid")
            try:
                # Elimina la vecchia immagine solo se diversa da quella default
                if (old_image and 
                    old_image.name != 'defaultProfileImage.jpg' and 
                    os.path.exists(old_image.path)):
                    # Elimina il file fisico
                    print(f"Deleting old image: {old_image.path}")
                    os.remove(old_image.path)
                
                form.save()
                print("Profile image updated successfully")
                messages.success(request, "Immagine aggiornata!")
                return redirect('profile', pk=self.object.id)
                
            except Exception as e:
                print(f"Error updating profile image: {str(e)}")
                messages.error(request, f"Errore: {str(e)}")
        else:
            print(f"Form is invalid: {form.errors}")
            messages.error(request, "Form non valido")

        context = self.get_context_data()
        context['profForm'] = form
        print("Rendering response with updated context")
        return self.render_to_response(context)

class LoopDetailView(DetailView):
    model = Loop
    template_name = 'loop_detail.html'
    context_object_name = 'loop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profImg'] = getattr(self.object.user, 'profileimage', None)
        return context
    
class SamplePackDetailView(DetailView):
    model = SamplePack
    template_name = 'user/samplepack_detail.html'
    context_object_name = 'samplepack'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profImg'] = getattr(self.object.user, 'profileimage', None)
        return context

class LoopsListView(ListView):
    model = Loop
    template_name = 'loops.html'
    context_object_name = 'loops'

class SamplePacksListView(ListView):
    model = SamplePack
    template_name = 'samplepacks.html'
    context_object_name = 'samplepacks'

@login_required
@require_POST
def remove_profile_image(request, pk=None):
    profile = request.user.profileimage
    profile.image.delete(save=False)  # elimina il file fisico
    profile.image = 'defaultProfileImage.jpg'  # imposta l'immagine predefinita
    profile.save()
    return redirect('profile', pk=pk)

@login_required
def upload(request):
    return render(request, 'user/upload.html')        

@login_required
def upload_loop(request):
    if request.method == 'POST':
        form = LoopForm(request.POST, request.FILES)
        if form.is_valid():
            loop = form.save(commit=False)
            loop.user = request.user
            loop.save()
            url = reverse('loop_detail', args=[loop.id])
            messages.success(
                request,
                f'Prodotto "{loop.title}" caricato con successo! <a href="{url}">Visualizza prodotto</a>',
                extra_tags='safe'
            )
            form = LoopForm()
    else:
        form = LoopForm()
    return render(request, 'user/upload_loop.html', {'form': form})

@login_required
def upload_samplepack(request):
    if request.method == 'POST':
        form = SamplePackForm(request.POST, request.FILES)
        if form.is_valid():
            loop = form.save(commit=False)
            loop.user = request.user
            loop.save()
            messages.success(request, 'SamplePack uploaded successfully!')
            return redirect('home')
    else:
        form = SamplePackForm()
    return render(request, 'user/upload_samplepack.html', {'form': form})

@login_required
@require_POST
def delete_upload_view(request, pk, modeltype):
    if modeltype == 'Loop':
        load = get_object_or_404(Loop, pk=pk, user=request.user)
    elif modeltype == 'SamplePack':
        load = get_object_or_404(SamplePack, pk=pk, user=request.user)
    else:
        messages.error(request, "Invalid model type.")
        return redirect('profile')

    load.delete()
    messages.success(request, f"{modeltype} deleted successfully!")
    return redirect('profile')

@login_required
@require_POST
def like_upload(request, pk, modeltype):
    if modeltype == 'Loop':
        load = get_object_or_404(Loop, pk=pk)
    elif modeltype == 'SamplePack':
        load = get_object_or_404(SamplePack, pk=pk)
    else:
        messages.error(request, "Invalid model type.")
        return redirect('home')

    if request.user in load.likes.all():
        load.likes.remove(request.user)
        messages.success(request, "You unliked this upload.")
    else:
        load.likes.add(request.user)
        messages.success(request, "You liked this upload.")

    return redirect('home')
