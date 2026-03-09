from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'testproj/home.html')

def events(request):
    return render(request, 'testproj/events.html')