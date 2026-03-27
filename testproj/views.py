import json
from datetime import date
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import BookingLog, DateEntry, NotesLog

# ── CONSTANTS ────────────────────────────────────────────────────────────────
VENUE_CHOICES = [
    ('birthday',      'Birthday & Private Venue'),
    ('wedding',       'Wedding & Romantic Venue'),
    ('family',        'Family Milestones Venue'),
    ('academic',      'Academic & Youth Venue'),
    ('corporate',     'Corporate & Formal Venue'),
    ('entertainment', 'Entertainment & Special Venue'),
]

# ── HELPERS ──────────────────────────────────────────────────────────────────
def _auto_update_time_based_statuses():
    today = date.today()
    DateEntry.objects.filter(status="booked", date=today).update(status="ongoing")
    DateEntry.objects.filter(status__in=["booked", "ongoing"], date__lt=today).update(status="done")

def _require_admin(request):
    return request.session.get("is_admin", False)

def _require_user(request):
    return bool(request.session.get("user_email"))

# ── PUBLIC VIEWS ─────────────────────────────────────────────────────────────
def home(request): return render(request, 'testproj/home.html')
def about(request): return render(request, 'testproj/about.html')
def book(request): return render(request, 'testproj/book.html')
def events(request): return render(request, 'testproj/events.html')
def log_in(request): return render(request, 'testproj/log_in.html')

def submit_booking(request):
    messages.success(request, "Your inquiry has been submitted successfully.")
    return redirect('home')

# ── ADMIN AUTH ───────────────────────────────────────────────────────────────
def custom_admin_login(request):
    if request.method == "POST":
        user = request.POST.get("username")
        passw = request.POST.get("password")
        if user == "admin" and passw == "admin123":
            request.session["is_admin"] = True
            request.session["admin_username"] = "Admin"
            return redirect("custom_admin_dashboard")
        messages.error(request, "Invalid credentials.")
    return render(request, "testproj/custom-admin/login.html")

def custom_admin_logout(request):
    request.session.flush()
    return redirect("custom_admin_login")

# ── ADMIN PANEL ──────────────────────────────────────────────────────────────
def custom_admin_dashboard(request):
    if not _require_admin(request): return redirect("custom_admin_login")
    _auto_update_time_based_statuses()
    context = {
        "booked_count": DateEntry.objects.filter(status="booked").count(),
        "unavailable_count": DateEntry.objects.filter(status="unavailable").count(),
        "upcoming": DateEntry.objects.filter(date__gte=date.today()).order_by("date")[:10],
        "recent_bookings": DateEntry.objects.exclude(email="").order_by("-id")[:5],
    }
    return render(request, "testproj/custom-admin/dashboard.html", context)

def custom_admin_dates(request):
    if not _require_admin(request): return redirect("custom_admin_login")
    venue_filter = request.GET.get('venue')
    qs = DateEntry.objects.all().order_by("date")
    if venue_filter:
        qs = qs.filter(venue=venue_filter)
    return render(request, "testproj/custom-admin/dates.html", {"dates": qs, "venue_choices": VENUE_CHOICES, "venue_filter": venue_filter})

def custom_admin_add_date(request):
    if not _require_admin(request): return redirect("custom_admin_login")
    if request.method == "POST":
        DateEntry.objects.create(
            venue=request.POST.get("venue"),
            date=request.POST.get("date"),
            status=request.POST.get("status"),
            event_name=request.POST.get("event_name"),
            pax=request.POST.get("pax") or None,
            time_slot=request.POST.get("time_slot"),
            notes=request.POST.get("notes")
        )
        return redirect("custom_admin_dates")
    return render(request, "testproj/custom-admin/add_date.html", {"venue_choices": VENUE_CHOICES})

def custom_admin_edit_date(request, pk):
    if not _require_admin(request): return redirect("custom_admin_login")
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == "POST":
        entry.venue = request.POST.get("venue")
        entry.date = request.POST.get("date")
        entry.status = request.POST.get("status")
        entry.event_name = request.POST.get("event_name")
        entry.pax = request.POST.get("pax") or None
        entry.time_slot = request.POST.get("time_slot")
        entry.notes = request.POST.get("notes")
        entry.save()
        return redirect("custom_admin_dates")
    return render(request, "testproj/custom-admin/edit_date.html", {"entry": entry, "venue_choices": VENUE_CHOICES})

def custom_admin_bookings(request):
    if not _require_admin(request): return redirect("custom_admin_login")
    bookings = DateEntry.objects.exclude(email=None).exclude(email="").order_by("-id")
    return render(request, "testproj/custom-admin/booking.html", {"bookings": bookings, "venue_choices": VENUE_CHOICES})

def custom_admin_calendar(request):
    if not _require_admin(request): return redirect("custom_admin_login")
    return render(request, "testproj/custom-admin/calendar.html")

# -- HELPERS --
def _require_user(request):
    return bool(request.session.get("user_email"))

# -- UPDATED LOGIN VIEW --
def log_in(request):
    if request.method == 'POST':
        # .strip() removes accidental spaces at the beginning or end
        email_input = request.POST.get('email', '').strip()
        
        # Look for the first booking matching this email (case-insensitive)
        booking = DateEntry.objects.filter(email__iexact=email_input).first()
        
        if booking:
            # Create session data
            request.session['user_email'] = booking.email
            request.session['user_name'] = booking.event_name
            return redirect('user_dashboard')
        else:
            # This triggers if the email isn't found in the DateEntry table
            messages.error(request, "No bookings found for this email. Please check your spelling or contact support.")
            return render(request, 'testproj/log_in.html')
            
    return render(request, 'testproj/log_in.html')

def user_logout(request):
    if 'user_email' in request.session:
        del request.session['user_email']
    if 'user_name' in request.session:
        del request.session['user_name']
    return redirect('home')

# -- USER PANEL VIEWS (Ensuring session check) --
def user_dashboard(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    
    bookings = DateEntry.objects.filter(email=email)
    context = {
        'total_bookings': bookings.count(),
        'upcoming_count': bookings.filter(status='booked').count(),
        'ongoing_count':  bookings.filter(status='ongoing').count(),
        'done_count':     bookings.filter(status='done').count(),
        'upcoming_list':  bookings.filter(status__in=['booked', 'rescheduled']).order_by('date')[:5],
    }
    return render(request, 'testproj/user-panel/user_dashboard.html', context)

def user_bookings(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
        
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
    
    booking = get_object_or_404(DateEntry, pk=pk, email=email)
    return render(request, 'testproj/user-panel/user_bookingdetails.html', {'booking': booking})

# ── VENUE VIEWS (ALL 6 VENUES) ───────────────────────────────────────────────

# 1. Birthday
def birthday_overview(request): return render(request, 'testproj/venues/birthday_overview.html')
def birthday_gallery(request): return render(request, 'testproj/venues/birthday_gallery.html')
def birthday_room(request): return render(request, 'testproj/venues/birthday_room.html')
def birthday_calendar(request): return render(request, 'testproj/venues/birthday_calendar.html')
def birthday_testimonials(request): return render(request, 'testproj/venues/birthday_testimonials.html')

# 2. Wedding
def wedding_overview(request): return render(request, 'testproj/wedding_overview.html')
def wedding_gallery(request): return render(request, 'testproj/wedding_gallery.html')
def wedding_room(request): return render(request, 'testproj/wedding_room.html')
def wedding_calendar(request): return render(request, 'testproj/venues/calendar.html')
def wedding_testimonials(request): return render(request, 'testproj/venues/testimonials.html')

# 3. Family
def family_overview(request): return render(request, 'testproj/venues/family_overview.html')
def family_gallery(request): return render(request, 'testproj/family_gallery.html')
def family_room(request): return render(request, 'testproj/family_room.html')
def family_calendar(request): return render(request, 'testproj/venues/calendar.html')
def family_testimonials(request): return render(request, 'testproj/venues/testimonials.html')

# 4. Academic
def academic_overview(request): return render(request, 'testproj/venues/academic_overview.html')
def academic_gallery(request): return render(request, 'testproj/venues/gallery.html')
def academic_room(request): return render(request, 'testproj/venues/room.html')
def academic_calendar(request): return render(request, 'testproj/venues/calendar.html')
def academic_testimonials(request): return render(request, 'testproj/venues/testimonials.html')

# 5. Corporate
def corporate_overview(request): return render(request, 'testproj/venues/corporate_overview.html')
def corporate_gallery(request): return render(request, 'testproj/venues/gallery.html')
def corporate_room(request): return render(request, 'testproj/venues/room.html')
def corporate_calendar(request): return render(request, 'testproj/venues/calendar.html')
def corporate_testimonials(request): return render(request, 'testproj/venues/testimonials.html')

# 6. Entertainment
def entertainment_overview(request): return render(request, 'testproj/venues/entertainment_overview.html')
def entertainment_gallery(request): return render(request, 'testproj/venues/gallery.html')
def entertainment_room(request): return render(request, 'testproj/venues/room.html')
def entertainment_calendar(request): return render(request, 'testproj/venues/calendar.html')
def entertainment_testimonials(request): return render(request, 'testproj/entertainment_testimonials.html')