from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView, UpdateView
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

    def get_object(self, queryset=None):
        # Recupera l'utente in base alla pk e verifica che corrisponda all'utente loggato
        obj = super().get_object(queryset)
        if obj.pk != self.request.user.pk:
            raise HttpResponseForbidden("Non hai il permesso di accedere a questa pagina.")
        return obj
   
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