from django.urls import path
from . import views

urlpatterns = [
    # ── General ──
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('book/', views.book, name='book'),
    path('events/', views.events, name='events'),
    path('login/', views.log_in, name='log_in'),
    path('submit-booking/', views.submit_booking, name='submit_booking'),

    # ── Admin Panel ──
    path('admin-panel/login/', views.custom_admin_login, name='custom_admin_login'),
    path('admin-panel/logout/', views.custom_admin_logout, name='custom_admin_logout'),
    path('admin-panel/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    path('admin-panel/dates/', views.custom_admin_dates, name='custom_admin_dates'),
    path('admin-panel/dates/add/', views.custom_admin_add_date, name='custom_admin_add_date'),
    path('admin-panel/dates/<int:pk>/edit/', views.custom_admin_edit_date, name='custom_admin_edit_date'),
    path('admin-panel/bookings/', views.custom_admin_bookings, name='custom_admin_bookings'),
    path('admin-panel/calendar/', views.custom_admin_calendar, name='custom_admin_calendar'),

    # ── User Panel (Pointed to the views above) ──
    path('my-account/', views.user_dashboard, name='user_dashboard'),
    path('my-account/bookings/', views.user_bookings, name='user_bookings'),
    path('my-account/bookings/<int:pk>/', views.user_booking_detail, name='user_booking_detail'),
    path('my-account/calendar/', views.user_calendar, name='user_calendar'),

    # ── Birthday ──
    path('events/birthday/', views.birthday_overview, name='birthday_overview'),
    path('events/birthday/gallery/', views.birthday_gallery, name='birthday_gallery'),
    path('events/birthday/room/', views.birthday_room, name='birthday_room'),
    path('events/birthday/calendar/', views.birthday_calendar, name='birthday_calendar'),
    path('events/birthday/testimonials/', views.birthday_testimonials, name='birthday_testimonials'),

    # ── Wedding ──
    path('events/wedding/', views.wedding_overview, name='wedding_overview'),
    path('events/wedding/gallery/', views.wedding_gallery, name='wedding_gallery'),
    path('events/wedding/room/', views.wedding_room, name='wedding_room'),
    path('events/wedding/calendar/', views.wedding_calendar, name='wedding_calendar'),
    path('events/wedding/testimonials/', views.wedding_testimonials, name='wedding_testimonials'),

    # ── Family ──
    path('events/family/', views.family_overview, name='family_overview'),
    path('events/family/gallery/', views.family_gallery, name='family_gallery'),
    path('events/family/room/', views.family_room, name='family_room'),
    path('events/family/calendar/', views.family_calendar, name='family_calendar'),
    path('events/family/testimonials/', views.family_testimonials, name='family_testimonials'),

    # ── Academic ──
    path('events/academic/', views.academic_overview, name='academic_overview'),
    path('events/academic/gallery/', views.academic_gallery, name='academic_gallery'),
    path('events/academic/room/', views.academic_room, name='academic_room'),
    path('events/academic/calendar/', views.academic_calendar, name='academic_calendar'),
    path('events/academic/testimonials/', views.academic_testimonials, name='academic_testimonials'),

    # ── Corporate ──
    path('events/corporate/', views.corporate_overview, name='corporate_overview'),
    path('events/corporate/gallery/', views.corporate_gallery, name='corporate_gallery'),
    path('events/corporate/room/', views.corporate_room, name='corporate_room'),
    path('events/corporate/calendar/', views.corporate_calendar, name='corporate_calendar'),
    path('events/corporate/testimonials/', views.corporate_testimonials, name='corporate_testimonials'),

    # ── Entertainment ──
    path('events/entertainment/', views.entertainment_overview, name='entertainment_overview'),
    path('events/entertainment/gallery/', views.entertainment_gallery, name='entertainment_gallery'),
    path('events/entertainment/room/', views.entertainment_room, name='entertainment_room'),
    path('events/entertainment/calendar/', views.entertainment_calendar, name='entertainment_calendar'),
    path('events/entertainment/testimonials/', views.entertainment_testimonials, name='entertainment_testimonials'),
]