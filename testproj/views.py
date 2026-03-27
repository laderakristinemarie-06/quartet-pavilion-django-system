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

def user_dashboard(request):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email)
    return render(request, 'testproj/user-panel/user_dashboard.html', {'bookings': bookings})

# ── VENUE VIEWS ──────────────────────────────────────────────────────────────
def birthday_overview(request): return render(request, 'testproj/venues/birthday_overview.html')
def birthday_calendar(request): return render(request, 'testproj/venues/birthday_calendar.html', _venue_calendar_context('birthday'))
# ... (Repeat similar pattern for other 5 venues as needed)

def user_bookings(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
        
    status_filter = request.GET.get('status')
    # Filter bookings based on the logged-in user's email
    bookings = DateEntry.objects.filter(email=email)
    
    if status_filter:
        bookings = bookings.filter(status=status_filter)
        
    return render(request, 'testproj/user-panel/user_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter
    })

# ── USER PANEL FUNCTIONS ─────────────────────────────────────────────────────

def user_bookings(request):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    status_filter = request.GET.get('status')
    bookings = DateEntry.objects.filter(email=email)
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'testproj/user-panel/user_bookings.html', {
        'bookings': bookings, 
        'status_filter': status_filter
    })

def user_calendar(request):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email)
    events_data = []
    for b in bookings:
        events_data.append({
            'date': b.date.isoformat(),
            'status': b.status,
            'venue': b.get_venue_display(),
            'pax': b.pax,
            'time_slot': b.time_slot
        })
    return render(request, 'testproj/user-panel/user_calendar.html', {
        'events_json': json.dumps(events_data)
    })

def user_booking_detail(request, pk):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    # This ensures users can only see THEIR OWN booking details
    booking = get_object_or_404(DateEntry, pk=pk, email=email)
    return render(request, 'testproj/user-panel/user_bookingdetails.html', {'booking': booking})

# ── ADMIN LOGOUT ──
def custom_admin_logout(request):
    request.session.flush()
    return redirect("custom_admin_login")

# ── USER CALENDAR (In case Django asks for it next) ──
def user_calendar(request):
    email = request.session.get('user_email')
    if not email: return redirect('log_in')
    
    bookings = DateEntry.objects.filter(email=email)
    events_data = []
    for b in bookings:
        events_data.append({
            'date': b.date.isoformat(),
            'status': b.status,
            'venue': b.get_venue_display() if hasattr(b, 'get_venue_display') else b.venue,
            'pax': b.pax,
            'time_slot': b.time_slot
        })
    return render(request, 'testproj/user-panel/user_calendar.html', {
        'events_json': json.dumps(events_data)
    })

# ── ADMIN DATE MANAGEMENT ──────────────────────────────────────────────────

def custom_admin_dates(request):
    # This view lists all the dates in the admin panel
    dates = DateEntry.objects.all().order_by('-date')
    return render(request, 'testproj/admin-panel/admin_dates.html', {'dates': dates})

# ── ADMIN MANAGEMENT ────────────────────────────────────────────────────────

def custom_admin_add_date(request):
    if request.method == "POST":
        date_val = request.POST.get('date')
        venue_val = request.POST.get('venue')
        status_val = request.POST.get('status', 'available')
        DateEntry.objects.create(date=date_val, venue=venue_val, status=status_val)
        return redirect('custom_admin_dates')
    return render(request, 'testproj/admin-panel/add_date.html')

def custom_admin_edit_date(request, pk):
    date_obj = get_object_or_404(DateEntry, pk=pk)
    if request.method == "POST":
        date_obj.date = request.POST.get('date')
        date_obj.venue = request.POST.get('venue')
        date_obj.status = request.POST.get('status')
        date_obj.save()
        return redirect('custom_admin_dates')
    return render(request, 'testproj/admin-panel/edit_date.html', {'date': date_obj})

def custom_admin_delete_date(request, pk):
    date_obj = get_object_or_404(DateEntry, pk=pk)
    if request.method == "POST":
        date_obj.delete()
        return redirect('custom_admin_dates')
    return render(request, 'testproj/admin-panel/delete_confirm.html', {'date': date_obj})

def custom_admin_inquiries(request):
    inquiries = BookingInquiry.objects.all().order_by('-submitted_at')
    return render(request, 'testproj/admin-panel/admin_inquiries.html', {'inquiries': inquiries})

def custom_admin_dashboard(request):
    total_dates = DateEntry.objects.count()
    pending_count = BookingInquiry.objects.filter(status='pending').count()
    return render(request, 'testproj/admin-panel/admin_dashboard.html', {
        'total_dates': total_dates,
        'pending_count': pending_count
    })

# ── INQUIRY ACTIONS ──

def custom_admin_approve_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'approve':
            # Create the actual booking in the calendar
            DateEntry.objects.create(
                date=inquiry.date,
                venue=inquiry.venue,
                event_name=inquiry.event_name,
                email=inquiry.email,
                pax=inquiry.pax,
                time_slot=inquiry.time_slot,
                status='booked'
            )
            inquiry.status = 'approved'
        elif action == 'reject':
            inquiry.status = 'rejected'
        
        inquiry.save()
        return redirect('custom_admin_inquiries')
    return render(request, 'testproj/admin-panel/approve_confirm.html', {'inquiry': inquiry})

def custom_admin_dashboard(request):
    total_dates = DateEntry.objects.count()
    pending_count = BookingInquiry.objects.filter(status='pending').count()
    return render(request, 'testproj/admin-panel/admin_dashboard.html', {
        'total_dates': total_dates,
        'pending_count': pending_count
    })

# ── ADMIN BOOKINGS & LOGS ──

def custom_admin_bookings(request):
    # Shows all confirmed bookings (DateEntry objects that are not 'available')
    bookings = DateEntry.objects.exclude(status='available').order_by('-date')
    return render(request, 'testproj/admin-panel/admin_bookings.html', {'bookings': bookings})

def custom_admin_logs(request):
    # Shows the history of actions taken in the system
    logs = BookingLog.objects.all().order_by('-timestamp')
    return render(request, 'testproj/admin-panel/admin_logs.html', {'logs': logs})

# ── ADMIN CALENDAR & NOTES ──

def custom_admin_calendar(request):
    # This collects all dates for the admin's master calendar
    dates = DateEntry.objects.all()
    events_data = []
    for d in dates:
        events_data.append({
            'date': d.date.isoformat(),
            'status': d.status,
            'venue': d.get_venue_display() if hasattr(d, 'get_venue_display') else d.venue,
            'event_name': d.event_name or "Available"
        })
    return render(request, 'testproj/admin-panel/admin_calendar.html', {
        'events_json': json.dumps(events_data)
    })

def custom_admin_notes(request):
    # Standard view for checking internal admin notes/logs
    notes = NotesLog.objects.all().order_by('-created_at')
    return render(request, 'testproj/admin-panel/admin_notes.html', {'notes': notes})

def birthday_overview(request):      return render(request, 'testproj/birthday_overview.html')

def birthday_gallery(request):       return render(request, 'testproj/birthday_gallery.html')

def birthday_room(request):          return render(request, 'testproj/birthday_room.html')

def birthday_calendar(request):      return render(request, 'testproj/birthday_calendar.html', _venue_calendar_context('birthday'))

def birthday_testimonials(request):  return render(request, 'testproj/birthday_testimonials.html')



def wedding_overview(request):       return render(request, 'testproj/wedding_overview.html')

def wedding_gallery(request):        return render(request, 'testproj/wedding_gallery.html')

def wedding_room(request):           return render(request, 'testproj/wedding_room.html')

def wedding_calendar(request):       return render(request, 'testproj/wedding_calendar.html', _venue_calendar_context('wedding'))

def wedding_testimonials(request):   return render(request, 'testproj/wedding_testimonials.html')



def family_overview(request):        return render(request, 'testproj/family_overview.html')

def family_gallery(request):         return render(request, 'testproj/family_gallery.html')

def family_room(request):            return render(request, 'testproj/family_room.html')

def family_calendar(request):        return render(request, 'testproj/family_calendar.html', _venue_calendar_context('family'))

def family_testimonials(request):    return render(request, 'testproj/family_testimonials.html')



def academic_overview(request):      return render(request, 'testproj/academic_overview.html')

def academic_gallery(request):       return render(request, 'testproj/academic_gallery.html')

def academic_room(request):          return render(request, 'testproj/academic_room.html')

def academic_calendar(request):      return render(request, 'testproj/academic_calendar.html', _venue_calendar_context('academic'))

def academic_testimonials(request):  return render(request, 'testproj/academic_testimonials.html')



def corporate_overview(request):     return render(request, 'testproj/corporate_overview.html')

def corporate_gallery(request):      return render(request, 'testproj/corporate_gallery.html')

def corporate_room(request):         return render(request, 'testproj/corporate_room.html')

def corporate_calendar(request):     return render(request, 'testproj/corporate_calendar.html', _venue_calendar_context('corporate'))

def corporate_testimonials(request): return render(request, 'testproj/corporate_testimonials.html')



def entertainment_overview(request):     return render(request, 'testproj/entertainment_overview.html')

def entertainment_gallery(request):      return render(request, 'testproj/entertainment_gallery.html')

def entertainment_room(request):         return render(request, 'testproj/entertainment_room.html')

def entertainment_calendar(request):     return render(request, 'testproj/entertainment_calendar.html', _venue_calendar_context('entertainment'))

def entertainment_testimonials(request): return render(request, 'testproj/entertainment_testimonials.html')