from django.urls import path
from . import views

urlpatterns = [
    path('',            views.home,        name='home'),
    path('about/',      views.about,       name='about'),
    path('book/',       views.book,        name='book'),
    path('events/',     views.events,      name='events'),
    path('login/',      views.log_in,      name='log_in'),
    #Birthday Venue
    path('events/birthday/',   views.birthday_overview,    name='birthday_overview'),
    path('events/birthday/gallery/',    views.birthday_gallery,     name='birthday_gallery'),
    path('events/birthday/room/',       views.birthday_room,        name='birthday_room'),
    path('events/birthday/calendar/',   views.birthday_calendar,             name='birthday_calendar'),
    path('events/birthday/testimonials/', views.birthday_testimonials, name='birthday_testimonials'),
    #Wedding Venue
    path('events/wedding/',      views.wedding_overview,       name='wedding_overview'),
    path('events/wedding/gallery/',      views.wedding_gallery,       name='wedding_gallery'),
    path('events/wedding/room/',      views.wedding_room,       name='wedding_room'),
    path('events/wedding/calendar/',      views.wedding_calendar,       name='wedding_calendar'),
    path('events/wedding/testimonials/',      views.wedding_testimonials,       name='wedding_testimonials'),
    #Family Venue
    path('events/family/',                    views.family_overview,        name='family_overview'),
    path('events/family/gallery/',             views.family_gallery,        name='family_gallery'),
    path('events/family/room/',                views.family_room,        name='family_room'),
    path('events/family/calendar/',             views.family_calendar,        name='family_calendar'),
    path('events/family/testimonials/',        views.family_testimonials,        name='family_testimonials'),
    #Academic & Youth Venue
    path('events/academic/',                      views.academic_overview,        name='academic_overview'),
    path('events/academic/gallery',               views.academic_gallery,       name='academic_gallery'),
    path('events/academic/room/',                 views.academic_room,       name='academic_room'),
    path('events/academic/calendar/',           views.academic_calendar,       name='academic_calendar'),
    path('events/academic/testimonials/',      views.academic_testimonials,       name='academic_testimonials'),
    #Corporate & Formal Venue
    path('events/corporate/',                views.corporate_overview,        name='corporate_overview'),
    path('events/corporate/gallery',                views.corporate_gallery,        name='corporate_gallery'),
    #Entertainment & Special Venue
    path('events/entertainment/',                views.entertainment_overview,        name='entertainment_overview'),
    path('events/entertainment/gallery',                views.entertainment_gallery,        name='entertainment_gallery'),

    path('submit-booking/', views.submit_booking, name='submit_booking'),
    path('admin/bookings/', views.custom_admin_bookings, name='custom_admin_bookings'),
    #Admin Panel
    path('manage/login/',    views.custom_admin_login,    name='custom_admin_login'),
    path('manage/logout/',   views.custom_admin_logout,   name='custom_admin_logout'),
    path('manage/',          views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('manage/dates/',    views.custom_admin_dates,    name='custom_admin_dates'),
    path('manage/dates/add/',         views.custom_admin_add_date,    name='custom_admin_add_date'),
    path('manage/dates/edit/<int:pk>/', views.custom_admin_edit_date, name='custom_admin_edit_date'),
    path('manage/dates/delete/<int:pk>/', views.custom_admin_delete_date, name='custom_admin_delete_date'),
    path('calendar/book/', views.submit_booking, name='submit_booking'),
    path('admin-panel/inquiries/', views.custom_admin_inquiries, name='custom_admin_inquiries'),
]