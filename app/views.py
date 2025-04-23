from django.http import HttpResponse
from django.shortcuts import render

def home(request, *args, **kwargs):
    tmp_name="home.html"
    return render(request,tmp_name)

def login(request, *args, **kwargs):
    tmp_name = "login.html"
    return render(request, tmp_name)

def signup(request, *args, **kwargs):
    tmp_name = "signup.html"
    return render(request, tmp_name)