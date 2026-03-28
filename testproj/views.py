import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
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

def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_email'):
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def _auto_update_time_based_statuses():
    today = date.today()
    DateEntry.objects.filter(status="booked", date=today).update(status="ongoing")
    DateEntry.objects.filter(status__in=["booked", "ongoing"], date__lt=today).update(status="done")

def _venue_calendar_context(venue_slug):
    booked = DateEntry.objects.filter(venue=venue_slug, status='booked').values('date', 'event_name', 'pax', 'time_slot')
    unavailable = DateEntry.objects.filter(venue=venue_slug, status='unavailable').values('date')
    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'venue_slug':        venue_slug,
    }

# ── PUBLIC VIEWS ─────────────────────────────────────────────────────────────
def home(request):   return render(request, 'testproj/home.html')
def about(request):  return render(request, 'testproj/about.html')
def events(request): return render(request, 'testproj/events.html')

def book(request):
    venue = request.GET.get('venue', 'birthday')
    return render(request, 'testproj/book.html', {
        'venue':      venue,
        'venue_name': VENUE_NAMES.get(venue, 'Quartet Pavilion'),
    })

def submit_booking(request):
    if request.method == 'POST':
        venue      = request.POST.get('venue', 'birthday')
        date_val   = request.POST.get('date')
        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        event_name = request.POST.get('event_name', '').strip()

        inquiry = BookingInquiry.objects.create(
            venue=venue, date=date_val, name=name, email=email,
            event_name=event_name, status='pending'
        )

        entry, created = DateEntry.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={
                'status':     'booked',
                'event_name': event_name,
                'email':      email,
                'pax':        request.POST.get('pax') or None,
                'time_slot':  request.POST.get('time_slot', ''),
            },
        )

        # Log the initial booking status
        BookingLog.objects.create(entry=entry, status='booked', note='Booking inquiry submitted.')

        try:
            subject = 'Booking Inquiry Received — Quartet Pavilion'
            msg = EmailMultiAlternatives(
                subject,
                f'Hi {name}, your inquiry has been received! We will confirm your booking shortly.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            msg.send(fail_silently=True)
        except Exception:
            pass

        messages.success(request, "Your inquiry has been submitted successfully.")
        return redirect('booking_receipt', pk=inquiry.pk)
    return redirect('home')

def booking_receipt(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    return render(request, 'testproj/booking_receipt.html', {
        'inquiry':    inquiry,
        'venue_name': VENUE_NAMES.get(inquiry.venue, inquiry.venue.title()),
    })

# ── ADMIN SECTION ────────────────────────────────────────────────────────────
def custom_admin_login(request):
    if request.method == 'POST':
        user  = request.POST.get('username')
        passw = request.POST.get('password')
        if user == "admin" and passw == "admin123":
            request.session['is_admin'] = True
            return redirect('custom_admin_dashboard')
        messages.error(request, "Invalid credentials.")
    return render(request, 'testproj/custom-admin/login.html')

def custom_admin_logout(request):
    request.session.pop('is_admin', None)
    return redirect('custom_admin_login')

@admin_required
def custom_admin_dashboard(request):
    _auto_update_time_based_statuses()
    context = {
        'booked_count':  DateEntry.objects.filter(status='booked').count(),
        'pending_count': BookingInquiry.objects.filter(status='pending').count(),
        'upcoming':      DateEntry.objects.filter(date__gte=date.today()).order_by('date')[:10],
    }
    return render(request, "testproj/custom-admin/dashboard.html", context)

@admin_required
def custom_admin_dates(request):
    entries = DateEntry.objects.all()
    return render(request, 'testproj/custom-admin/dates.html', {'entries': entries})

@admin_required
def custom_admin_add_date(request):
    if request.method == 'POST':
        DateEntry.objects.create(
            venue=request.POST.get('venue'),
            date=request.POST.get('date'),
            event_name=request.POST.get('event_name', ''),
            pax=request.POST.get('pax') or None,
            time_slot=request.POST.get('time_slot', ''),
            status=request.POST.get('status', 'booked'),
            email=request.POST.get('email', ''),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, "Date entry added.")
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/add_date.html', {
        'venue_choices':  DateEntry._meta.get_field('venue').choices,
        'status_choices': DateEntry._meta.get_field('status').choices,
    })

@admin_required
def custom_admin_edit_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        entry.venue      = request.POST.get('venue', entry.venue)
        entry.date       = request.POST.get('date', entry.date)
        entry.event_name = request.POST.get('event_name', entry.event_name)
        entry.pax        = request.POST.get('pax') or None
        entry.time_slot  = request.POST.get('time_slot', entry.time_slot)
        entry.status     = request.POST.get('status', entry.status)
        entry.email      = request.POST.get('email', entry.email)
        entry.notes      = request.POST.get('notes', entry.notes)
        entry.save()
        messages.success(request, "Date entry updated.")
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/edit_date.html', {
        'entry':          entry,
        'venue_choices':  DateEntry._meta.get_field('venue').choices,
        'status_choices': DateEntry._meta.get_field('status').choices,
    })

@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Date entry deleted.")
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/delete_date.html', {'entry': entry})

@admin_required
def custom_admin_inquiries(request):
    inquiries = BookingInquiry.objects.all()
    return render(request, 'testproj/custom-admin/inquiries.html', {'inquiries': inquiries})

@admin_required
def custom_admin_approve_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('approved', 'rejected', 'canceled'):
            inquiry.status = action
            inquiry.save()
            messages.success(request, f"Inquiry marked as {action}.")
        return redirect('custom_admin_inquiries')
    return render(request, 'testproj/custom-admin/inquiry_action.html', {'inquiry': inquiry})

@admin_required
def custom_admin_bookings(request):
    bookings = DateEntry.objects.exclude(status='available')
    return render(request, 'testproj/custom-admin/bookings.html', {'bookings': bookings})

@admin_required
def custom_admin_calendar(request):
    _auto_update_time_based_statuses()
    all_entries = DateEntry.objects.all().values('date', 'venue', 'event_name', 'status', 'pax', 'time_slot')
    return render(request, 'testproj/custom-admin/calendar.html', {
        'all_entries': json.dumps(list(all_entries), cls=DjangoJSONEncoder),
    })

# ── USER PANEL ───────────────────────────────────────────────────────────────
def user_login(request):
    """Guest portal login — looks up bookings by email."""
    if request.method == 'POST':
        email_input = request.POST.get('email', '').strip()
        booking = DateEntry.objects.filter(email__iexact=email_input).first()
        if booking:
            request.session['user_email'] = booking.email
            return redirect('user_dashboard')
        messages.error(request, "No bookings found for this email address.")
    return render(request, 'testproj/user-panel/user_login.html')

# Alias so old {% url 'log_in' %} links still work
def log_in(request):
    return user_login(request)

def user_logout(request):
    request.session.pop('user_email', None)
    return redirect('user_login')

@user_required
def user_dashboard(request):
    _auto_update_time_based_statuses()
    email    = request.session.get('user_email')
    bookings = DateEntry.objects.filter(email=email)
    today    = date.today()
    upcoming = bookings.filter(date__gte=today).exclude(status__in=['canceled', 'done'])

    return render(request, 'testproj/user-panel/user_dashboard.html', {
        'bookings':          bookings,
        'total_bookings':    bookings.count(),
        'upcoming_count':    upcoming.count(),
        'ongoing_count':     bookings.filter(status='ongoing').count(),
        'done_count':        bookings.filter(status='done').count(),
        'upcoming_bookings': upcoming.order_by('date')[:5],
    })

@user_required
def user_bookings(request):
    _auto_update_time_based_statuses()
    email         = request.session.get('user_email')
    status_filter = request.GET.get('status', '').strip()
    bookings      = DateEntry.objects.filter(email=email)

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'testproj/user-panel/user_bookings.html', {
        'bookings':      bookings.order_by('-date'),
        'status_filter': status_filter,
    })

@user_required
def user_booking_detail(request, pk):
    _auto_update_time_based_statuses()
    email   = request.session.get('user_email')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)
    history = BookingLog.objects.filter(entry=booking).order_by('changed_at')

    return render(request, 'testproj/user-panel/user_bookingdetails.html', {
        'booking':        booking,
        'status_history': history,
        'today_str':      date.today().isoformat(),
    })

@user_required
def user_booking_reschedule(request, pk):
    """Guest submits a reschedule request."""
    email   = request.session.get('user_email')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)

    if request.method == 'POST':
        new_date = request.POST.get('new_date', '').strip()
        reason   = request.POST.get('reschedule_reason', '').strip()

        if not new_date:
            messages.error(request, "Please select a new date.")
            return redirect('user_booking_detail', pk=pk)

        # Check the new date isn't already taken for this venue
        if DateEntry.objects.filter(venue=booking.venue, date=new_date).exclude(pk=pk).exists():
            messages.error(request, "That date is already taken for this venue. Please choose another.")
            return redirect('user_booking_detail', pk=pk)

        old_date             = booking.date
        booking.old_date     = old_date
        booking.date         = new_date
        booking.reschedule_reason = reason
        booking.status       = 'rescheduled'
        booking.save()

        BookingLog.objects.create(
            entry=booking,
            status='rescheduled',
            note=f'Reschedule requested from {old_date} to {new_date}. Reason: {reason or "—"}',
        )

        messages.success(request, f"Reschedule request submitted for {new_date}. We'll confirm within 24 hours.")

    return redirect('user_booking_detail', pk=pk)

@user_required
def user_booking_cancel(request, pk):
    """Guest cancels their own booking."""
    email   = request.session.get('user_email')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)

    if request.method == 'POST':
        if booking.status in ('booked', 'rescheduled'):
            booking.status = 'canceled'
            booking.save()

            BookingLog.objects.create(
                entry=booking,
                status='canceled',
                note='Booking canceled by guest.',
            )

            messages.success(request, "Your booking has been canceled.")
        else:
            messages.error(request, "This booking cannot be canceled at its current status.")

    return redirect('user_booking_detail', pk=pk)

@user_required
def user_calendar(request):
    _auto_update_time_based_statuses()
    email   = request.session.get('user_email')
    entries = DateEntry.objects.filter(email=email)

    bookings_data = []
    for e in entries:
        bookings_data.append({
            'date':        e.date.isoformat(),
            'venue':       e.venue,
            'venue_label': e.get_venue_display(),
            'event_name':  e.event_name,
            'status':      e.status,
            'pax':         e.pax,
            'time_slot':   e.time_slot,
            'detailUrl':   reverse('user_booking_detail', args=[e.pk]),
        })

    return render(request, 'testproj/user-panel/user_calendar.html', {
        'bookings_json': json.dumps(bookings_data),
    })

# ── VENUE VIEWS ───────────────────────────────────────────────────────────────
# Birthday
def birthday_overview(request):     return render(request, 'testproj/birthday_overview.html')
def birthday_gallery(request):      return render(request, 'testproj/birthday_gallery.html')
def birthday_room(request):         return render(request, 'testproj/birthday_room.html')
def birthday_calendar(request):     return render(request, 'testproj/birthday_calendar.html', _venue_calendar_context('birthday'))
def birthday_testimonials(request): return render(request, 'testproj/birthday_testimonials.html')

# Wedding
def wedding_overview(request):     return render(request, 'testproj/wedding_overview.html')
def wedding_gallery(request):      return render(request, 'testproj/wedding_gallery.html')
def wedding_room(request):         return render(request, 'testproj/wedding_room.html')
def wedding_calendar(request):     return render(request, 'testproj/wedding_calendar.html', _venue_calendar_context('wedding'))
def wedding_testimonials(request): return render(request, 'testproj/wedding_testimonials.html')

# Family
def family_overview(request):     return render(request, 'testproj/family_overview.html')
def family_gallery(request):      return render(request, 'testproj/family_gallery.html')
def family_room(request):         return render(request, 'testproj/family_room.html')
def family_calendar(request):     return render(request, 'testproj/family_calendar.html', _venue_calendar_context('family'))
def family_testimonials(request): return render(request, 'testproj/family_testimonials.html')

# Academic
def academic_overview(request):     return render(request, 'testproj/academic_overview.html')
def academic_gallery(request):      return render(request, 'testproj/academic_gallery.html')
def academic_room(request):         return render(request, 'testproj/academic_room.html')
def academic_calendar(request):     return render(request, 'testproj/academic_calendar.html', _venue_calendar_context('academic'))
def academic_testimonials(request): return render(request, 'testproj/academic_testimonials.html')

# Corporate
def corporate_overview(request):     return render(request, 'testproj/corporate_overview.html')
def corporate_gallery(request):      return render(request, 'testproj/corporate_gallery.html')
def corporate_room(request):         return render(request, 'testproj/corporate_room.html')
def corporate_calendar(request):     return render(request, 'testproj/corporate_calendar.html', _venue_calendar_context('corporate'))
def corporate_testimonials(request): return render(request, 'testproj/corporate_testimonials.html')

# Entertainment
def entertainment_overview(request):     return render(request, 'testproj/entertainment_overview.html')
def entertainment_gallery(request):      return render(request, 'testproj/entertainment_gallery.html')
def entertainment_room(request):         return render(request, 'testproj/entertainment_room.html')
def entertainment_calendar(request):     return render(request, 'testproj/entertainment_calendar.html', _venue_calendar_context('entertainment'))
def entertainment_testimonials(request): return render(request, 'testproj/entertainment_testimonials.html')