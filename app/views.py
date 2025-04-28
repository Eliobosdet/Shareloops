from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomRegisterForm, CustomLoginForm, UserUpdateForm
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.views.generic import DetailView
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
    return render(request, 'register.html', {'form': form})

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
    return render(request, 'login.html', {'form': form})


def logout_view(request, *args, **kwargs):
    logout(request)
    return redirect('home')

def profile_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'user': request.user})
    else:
        return redirect('login')

class UserDetailView(DetailView):
    model = User # Model to be used for the view
    template_name = 'profile.html' 
    context_object_name = 'user' # Name of the context variable to be used in the template

    def get_object(self, queryset=None):
        obj = get_object_or_404(User, pk=self.kwargs['pk'])
        if obj != self.request.user:
            raise Http404("Non puoi accedere al profilo di un altro utente.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = PasswordChangeForm(self.request.user)
        context['update_form'] = UserUpdateForm(instance=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if 'update_profile' in request.POST:
            update_form = UserUpdateForm(request.POST, instance=request.user)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, 'Profilo aggiornato con successo!')
                return redirect('profile', pk=request.user.pk)
            else:
                password_form = PasswordChangeForm(request.user)
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password cambiata con successo!')
                return redirect('profile', pk=request.user.pk)
            else:
                update_form = UserUpdateForm(instance=request.user)
        else:
            update_form = UserUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(request.user)

        context = self.get_context_data()
        context['update_form'] = update_form
        context['password_form'] = password_form
        return self.render_to_response(context)