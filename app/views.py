from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CustomRegisterForm

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
            return redirect('home')  # Assicurati che esista l'URL di nome 'login'
    else:
        form = CustomRegisterForm()
    return render(request, 'register.html', {'form': form})