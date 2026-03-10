from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events, name='events'),
    path('overview/', views.overview, name='overview'),  
    path('gallery/', views.gallery, name='gallery'),
    path('room/', views.room, name='room'),
    path('calendar/', views.calendar, name='calendar'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('book/', views.book, name='book'),
    path('login/', views.login, name='login'),
]