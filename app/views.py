from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CustomRegisterForm, CustomLoginForm
from django.contrib.auth import login
# from django.contrib.auth.forms import AuthenticationForm

def home(request, *args, **kwargs):
    tmp_name="home.html"
    return render(request,tmp_name)

def login(request, *args, **kwargs):
    tmp_name = "login.html"
    return render(request, tmp_name)

def register(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CustomRegisterForm()
    return render(request, 'register.html', {'form': form})

def login(request, *args, **kwargs):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})