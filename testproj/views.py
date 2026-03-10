from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    return render(request, 'testproj/home.html')

def events(request):
    return render(request, 'testproj/events.html')

def overview(request):
    return render(request, 'testproj/overview.html')

def wedding(request):                                      
    return render(request, 'testproj/wedding.html')

def gallery(request):
    return render(request, 'testproj/gallery.html')

def room(request):
    return render(request, 'testproj/room.html')

def calendar(request):
    return render(request, 'testproj/calendar.html')

def testimonials(request):
    return render(request, 'testproj/testimonials.html')

def book(request):
    return render(request, 'testproj/book.html')

def login(request):
    return render(request, 'testproj/login.html')