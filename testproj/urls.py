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
    path('login/', views.login, name='log_in'),
    path('manage/login/', views.custom_admin_login, name='custom_admin_login'),
    path('manage/logout/', views.custom_admin_logout, name='custom_admin_logout'),
    path('manage/dashboard/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('manage/dates/', views.custom_admin_dates, name='custom_admin_dates'),
    path('manage/dates/add/', views.custom_admin_add_date, name='custom_admin_add_date'),
    path('manage/dates/edit/<int:pk>/', views.custom_admin_edit_date, name='custom_admin_edit_date'),
    path('manage/dates/delete/<int:pk>/', views.custom_admin_delete_date, name='custom_admin_delete_date'),
]