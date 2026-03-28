from django.urls import path
from . import views

urlpatterns = [

    # ── General ──────────────────────────────────────────────────────────
    path('',        views.home,   name='home'),
    path('about/',  views.about,  name='about'),
    path('book/',   views.book,   name='book'),
    path('events/', views.events, name='events'),
    path('login/',  views.log_in, name='log_in'),

    # ── Booking ───────────────────────────────────────────────────────────
    path('submit-booking/',           views.submit_booking,  name='submit_booking'),
    path('booking/receipt/<int:pk>/', views.booking_receipt, name='booking_receipt'),

    # ── User Panel / My Account ───────────────────────────────────────────
    path('my-account/',                   views.user_dashboard,      name='user_dashboard'),
    path('my-account/bookings/',          views.user_bookings,       name='user_bookings'),
    path('my-account/bookings/<int:pk>/', views.user_booking_detail, name='user_booking_detail'),
    path('my-account/calendar/',          views.user_calendar,       name='user_calendar'),

    # ── Admin Panel ───────────────────────────────────────────────────────
    path('manage/',                             views.custom_admin_dashboard,      name='custom_admin_dashboard'),
    path('manage/login/',                       views.custom_admin_login,          name='custom_admin_login'),
    path('manage/logout/',                      views.custom_admin_logout,         name='custom_admin_logout'),
    path('manage/dates/',                       views.custom_admin_dates,          name='custom_admin_dates'),
    path('manage/dates/add/',                   views.custom_admin_add_date,       name='custom_admin_add_date'),
    path('manage/dates/edit/<int:pk>/',         views.custom_admin_edit_date,      name='custom_admin_edit_date'),
    path('manage/dates/delete/<int:pk>/',       views.custom_admin_delete_date,    name='custom_admin_delete_date'),
    path('manage/inquiries/',                   views.custom_admin_inquiries,      name='custom_admin_inquiries'),
    path('manage/inquiries/<int:pk>/action/',   views.custom_admin_approve_inquiry,name='custom_admin_approve_inquiry'),
    path('manage/bookings/',                    views.custom_admin_bookings,       name='custom_admin_bookings'),
    path('manage/calendar/',                    views.custom_admin_calendar,       name='custom_admin_calendar'),
    # Legacy path kept for team members using old prefix
    path('admin-panel/calendar/',               views.custom_admin_calendar,       name='custom_admin_calendar_legacy'),

    # ── Birthday Venue ────────────────────────────────────────────────────
    path('events/birthday/',              views.birthday_overview,     name='birthday_overview'),
    path('events/birthday/gallery/',      views.birthday_gallery,      name='birthday_gallery'),
    path('events/birthday/room/',         views.birthday_room,         name='birthday_room'),
    path('events/birthday/calendar/',     views.birthday_calendar,     name='birthday_calendar'),
    path('events/birthday/testimonials/', views.birthday_testimonials, name='birthday_testimonials'),

    # ── Wedding Venue ─────────────────────────────────────────────────────
    path('events/wedding/',              views.wedding_overview,     name='wedding_overview'),
    path('events/wedding/gallery/',      views.wedding_gallery,      name='wedding_gallery'),
    path('events/wedding/room/',         views.wedding_room,         name='wedding_room'),
    path('events/wedding/calendar/',     views.wedding_calendar,     name='wedding_calendar'),
    path('events/wedding/testimonials/', views.wedding_testimonials, name='wedding_testimonials'),

    # ── Family Venue ──────────────────────────────────────────────────────
    path('events/family/',              views.family_overview,     name='family_overview'),
    path('events/family/gallery/',      views.family_gallery,      name='family_gallery'),
    path('events/family/room/',         views.family_room,         name='family_room'),
    path('events/family/calendar/',     views.family_calendar,     name='family_calendar'),
    path('events/family/testimonials/', views.family_testimonials, name='family_testimonials'),

    # ── Academic Venue ────────────────────────────────────────────────────
    path('events/academic/',              views.academic_overview,     name='academic_overview'),
    path('events/academic/gallery/',      views.academic_gallery,      name='academic_gallery'),
    path('events/academic/room/',         views.academic_room,         name='academic_room'),
    path('events/academic/calendar/',     views.academic_calendar,     name='academic_calendar'),
    path('events/academic/testimonials/', views.academic_testimonials, name='academic_testimonials'),

    # ── Corporate Venue ───────────────────────────────────────────────────
    path('events/corporate/',              views.corporate_overview,     name='corporate_overview'),
    path('events/corporate/gallery/',      views.corporate_gallery,      name='corporate_gallery'),
    path('events/corporate/room/',         views.corporate_room,         name='corporate_room'),
    path('events/corporate/calendar/',     views.corporate_calendar,     name='corporate_calendar'),
    path('events/corporate/testimonials/', views.corporate_testimonials, name='corporate_testimonials'),

    # ── Entertainment Venue ───────────────────────────────────────────────
    path('events/entertainment/',              views.entertainment_overview,     name='entertainment_overview'),
    path('events/entertainment/gallery/',      views.entertainment_gallery,      name='entertainment_gallery'),
    path('events/entertainment/room/',         views.entertainment_room,         name='entertainment_room'),
    path('events/entertainment/calendar/',     views.entertainment_calendar,     name='entertainment_calendar'),
    path('events/entertainment/testimonials/', views.entertainment_testimonials, name='entertainment_testimonials'),

]