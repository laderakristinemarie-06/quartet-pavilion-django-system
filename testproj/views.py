import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

# Ensure these model names match your models.py exactly
from .models import DateEntry, BookingInquiry, BookingLog, NotesLog

# ── CONSTANTS ────────────────────────────────────────────────────────────────
VENUE_NAMES = {
    'birthday':      'Birthday & Private Venue',
    'wedding':       'Wedding & Romantic Venue',
    'family':        'Family Milestones Venue',
    'academic':      'Academic & Youth Venue',
    'corporate':     'Corporate & Formal Venue',
    'entertainment': 'Entertainment & Special Venue',
}

# ── DECORATORS & HELPERS ─────────────────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def _auto_update_time_based_statuses():
    today = date.today()
    DateEntry.objects.filter(status="booked", date=today).update(status="ongoing")
    DateEntry.objects.filter(status__in=["booked", "ongoing"], date__lt=today).update(status="done")

def _venue_calendar_context(venue_slug):
    booked = DateEntry.objects.filter(venue=venue_slug, status='booked').values('date','event_name','pax','time_slot')
    unavailable = DateEntry.objects.filter(venue=venue_slug, status='unavailable').values('date')
    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'venue_slug':         venue_slug,
    }

# ── PUBLIC VIEWS ─────────────────────────────────────────────────────────────
def home(request):   return render(request, 'testproj/home.html')
def about(request):  return render(request, 'testproj/about.html')
def events(request): return render(request, 'testproj/events.html')

def book(request):
    venue = request.GET.get('venue', 'birthday')
    return render(request, 'testproj/book.html', {
        'venue': venue,
        'venue_name': VENUE_NAMES.get(venue, 'Quartet Pavilion'),
    })

def submit_booking(request):
    if request.method == 'POST':
        venue = request.POST.get('venue', 'birthday')
        date_val = request.POST.get('date')
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        event_name = request.POST.get('event_name', '').strip()
        
        # Create Inquiry Record
        inquiry = BookingInquiry.objects.create(
            venue=venue, date=date_val, name=name, email=email,
            event_name=event_name, status='pending'
        )

        # Create/Update DateEntry (The actual calendar slot)
        DateEntry.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={
                'status': 'booked', 
                'event_name': event_name, 
                'email': email,
                'pax': request.POST.get('pax') or None,
                'time_slot': request.POST.get('time_slot', '')
            },
        )

        # Email logic (Simplified for stability)
        try:
            subject = f'Booking Inquiry Received — Quartet Pavilion'
            msg = EmailMultiAlternatives(subject, f'Hi {name}, received!', settings.DEFAULT_FROM_EMAIL, [email])
            msg.send(fail_silently=True)
        except: pass

        messages.success(request, "Your inquiry has been submitted successfully.")
        return redirect('booking_receipt', pk=inquiry.pk)
    return redirect('home')

def booking_receipt(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    return render(request, 'testproj/booking_receipt.html', {
        'inquiry': inquiry,
        'venue_name': VENUE_NAMES.get(inquiry.venue, inquiry.venue.title()),
    })

# ── ADMIN SECTION ────────────────────────────────────────────────────────────
def custom_admin_login(request):
    if request.method == 'POST':
        user = request.POST.get('username')
        passw = request.POST.get('password')
        # Simple auth check (Change this to real Django auth if needed)
        if user == "admin" and passw == "admin123":
            request.session['is_admin'] = True
            return redirect('custom_admin_dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, 'testproj/custom-admin/login.html')

@admin_required
def custom_admin_dashboard(request):
    _auto_update_time_based_statuses()
    context = {
        'booked_count': DateEntry.objects.filter(status='booked').count(),
        'pending_count': BookingInquiry.objects.filter(status='pending').count(),
        'upcoming': DateEntry.objects.filter(date__gte=date.today()).order_by('date')[:10],
    }
    return render(request, "testproj/custom-admin/dashboard.html", context)

# ── USER PANEL ───────────────────────────────────────────────────────────────
def log_in(request):
    if request.method == 'POST':
        email_input = request.POST.get('email', '').strip()
        booking = DateEntry.objects.filter(email__iexact=email_input).first()
        if booking:
            request.session['user_email'] = booking.email
            return redirect('user_dashboard')
        messages.error(request, "No bookings found for this email.")
    return render(request, 'testproj/log_in.html')

@property
def user_dashboard(request):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email)
    return render(request, 'testproj/user-panel/user_dashboard.html', {'bookings': bookings})

# ── VENUE VIEWS ──────────────────────────────────────────────────────────────
def birthday_overview(request): return render(request, 'testproj/venues/birthday_overview.html')
def birthday_calendar(request): return render(request, 'testproj/venues/birthday_calendar.html', _venue_calendar_context('birthday'))
# ... (Repeat similar pattern for other 5 venues as needed)