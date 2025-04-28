from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CustomRegisterForm, CustomLoginForm
from django.contrib.auth import login, logout
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