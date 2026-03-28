import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from testproj.models import DateEntry, BookingInquiry

# ── CONSTANTS ────────────────────────────────────────────────────────────────
VENUE_NAMES = {
    'birthday':      'Birthday & Private Venue',
    'wedding':       'Wedding & Romantic Venue',
    'family':        'Family Milestones Venue',
    'academic':      'Academic & Youth Venue',
    'corporate':     'Corporate & Formal Venue',
    'entertainment': 'Entertainment & Special Venue',
}

VENUE_CHOICES = DateEntry.VENUE_CHOICES

# ── DECORATORS & HELPERS ─────────────────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def _venue_calendar_context(venue_slug):
    booked = DateEntry.objects.filter(
        venue=venue_slug, status='booked'
    ).values('date', 'event_name', 'pax', 'time_slot')
    unavailable = DateEntry.objects.filter(
        venue=venue_slug, status='unavailable'
    ).values('date')
    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'venue_slug':        venue_slug,
    }

# ── GENERAL VIEWS ─────────────────────────────────────────────────────────────
def home(request):
    return render(request, 'testproj/home.html')

def about(request):
    return render(request, 'testproj/about.html')

def events(request):
    return render(request, 'testproj/events.html')

def book(request):
    venue    = request.GET.get('venue', 'birthday')
    next_url = request.GET.get('next', '/')
    return render(request, 'testproj/book.html', {
        'venue':      venue,
        'venue_name': VENUE_NAMES.get(venue, 'Quartet Pavilion'),
        'next_url':   next_url,
    })

def log_in(request):
    if request.method == 'POST':
        email_input = request.POST.get('email', '').strip()
        booking = DateEntry.objects.filter(email__iexact=email_input).first()
        if booking:
            request.session['user_email'] = booking.email
            return redirect('user_dashboard')
        messages.error(request, "No bookings found for this email.")
    return render(request, 'testproj/log_in.html')

# ── BOOKING SUBMISSION ────────────────────────────────────────────────────────
def submit_booking(request):
    if request.method == 'POST':
        venue            = request.POST.get('venue', 'birthday')
        date_val         = request.POST.get('date')
        name             = request.POST.get('name', '').strip()
        email            = request.POST.get('email', '').strip()
        phone            = request.POST.get('phone', '').strip()
        event_name       = request.POST.get('event_name', '').strip()
        pax              = request.POST.get('pax') or None
        time_slot        = request.POST.get('time_slot', '').strip()
        notes            = request.POST.get('notes', '').strip()
        payment          = request.POST.get('payment', '').strip()
        account_number   = request.POST.get('account_number', '').strip()
        reference_number = request.POST.get('reference_number', '').strip()
        start_time       = request.POST.get('start_time', '').strip()
        end_time         = request.POST.get('end_time', '').strip()
        departure_date   = request.POST.get('departure_date', '').strip() or None
        total_price      = request.POST.get('total_price', '0').strip()
        downpay_amount   = request.POST.get('downpay_amount', '0').strip()

        # Save inquiry
        inquiry = BookingInquiry.objects.create(
             venue=venue, date=date_val, name=name, email=email,
             event_name=event_name, pax=pax, time_slot=time_slot,
        )

        # Mark date as booked on the calendar immediately
        DateEntry.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={
                'status':     'booked',
                'event_name': event_name,
                'email':      email,
                'pax':        pax,
                'time_slot':  time_slot,
                'notes':      notes,
            },
        )

        # Email context
        ctx = {
            'inquiry':          inquiry,
            'name':             name,
            'email':            email,
            'phone':            phone,
            'venue_name':       VENUE_NAMES.get(venue, venue.title()),
            'event_name':       event_name,
            'date':             date_val,
            'departure_date':   departure_date,
            'start_time':       start_time,
            'end_time':         end_time,
            'pax':              pax,
            'time_slot':        time_slot,
            'payment':          payment,
            'account_number':   account_number,
            'reference_number': reference_number,
            'total_price':      total_price,
            'downpay_amount':   downpay_amount,
            'notes':            notes,
            'is_walkin':        payment == 'walkin',
            'booking_id':       f'QP-{inquiry.pk:05d}',
        }

        # Send email to client
        try:
            msg = EmailMultiAlternatives(
                subject    = f'Booking Inquiry Received — Quartet Pavilion ({ctx["booking_id"]})',
                body       = f'Hi {name}, your inquiry has been received. Booking ID: {ctx["booking_id"]}',
                from_email = settings.DEFAULT_FROM_EMAIL,
                to         = [email],
            )
            msg.attach_alternative(
                render_to_string('testproj/emails/booking_client.html', ctx), 'text/html'
            )
            msg.send(fail_silently=True)
        except Exception:
            pass

        # Send email to admin
        try:
            msg2 = EmailMultiAlternatives(
                subject    = f'New Booking — {name} | {VENUE_NAMES.get(venue, venue)} | {date_val}',
                body       = f'New booking inquiry from {name} for {date_val}.',
                from_email = settings.DEFAULT_FROM_EMAIL,
                to         = [settings.ADMIN_EMAIL],
            )
            msg2.attach_alternative(
                render_to_string('testproj/emails/booking_admin.html', ctx), 'text/html'
            )
            msg2.send(fail_silently=True)
        except Exception:
            pass

        messages.success(request, "Your inquiry has been submitted successfully.")
        return redirect('booking_receipt', pk=inquiry.pk)

    return redirect('home')

# ── BOOKING RECEIPT ───────────────────────────────────────────────────────────
def booking_receipt(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    return render(request, 'testproj/booking_receipt.html', {
        'inquiry':    inquiry,
        'venue_name': VENUE_NAMES.get(inquiry.venue, inquiry.venue.title()),
        'booking_id': f'QP-{inquiry.pk:05d}',
    })

# ── USER PANEL ────────────────────────────────────────────────────────────────
def user_dashboard(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email)
    return render(request, 'testproj/user-panel/user_dashboard.html', {
        'bookings': bookings
    })

def user_bookings(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    status_filter = request.GET.get('status')
    bookings = DateEntry.objects.filter(email=email)
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    return render(request, 'testproj/user-panel/user_bookings.html', {
        'bookings':      bookings,
        'status_filter': status_filter,
    })

def user_booking_detail(request, pk):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)
    return render(request, 'testproj/user-panel/user_bookingdetails.html', {
        'booking': booking
    })

def user_calendar(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email)
    events_data = []
    for b in bookings:
        events_data.append({
            'date':      b.date.isoformat(),
            'status':    b.status,
            'venue':     VENUE_NAMES.get(b.venue, b.venue),
            'pax':       b.pax,
            'time_slot': b.time_slot,
        })
    return render(request, 'testproj/user-panel/user_calendar.html', {
        'events_json': json.dumps(events_data)
    })

# ── ADMIN AUTH ────────────────────────────────────────────────────────────────
def custom_admin_login(request):
    if request.session.get('is_admin'):
        return redirect('custom_admin_dashboard')
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', '')
        )
        if user is not None and user.is_staff:
            request.session['is_admin']       = True
            request.session['admin_username'] = user.username
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'testproj/custom-admin/login.html')

def custom_admin_logout(request):
    request.session.flush()
    return redirect('custom_admin_login')

# ── ADMIN DASHBOARD ───────────────────────────────────────────────────────────
@admin_required
def custom_admin_dashboard(request):
    today = date.today()
    context = {
        'booked_count':      DateEntry.objects.filter(status='booked').count(),
        'unavailable_count': DateEntry.objects.filter(status='unavailable').count(),
        'pending_count':     BookingInquiry.objects.filter(status='pending').count(),
        'new_inquiries':     BookingInquiry.objects.filter(is_read=False).count(),
        'upcoming':          DateEntry.objects.filter(
                                 status='booked', date__gte=today
                             ).order_by('date')[:10],
        'recent_inquiries':  BookingInquiry.objects.filter(
                                 status='pending'
                             ).order_by('-submitted_at')[:5],
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)

# ── ADMIN DATES ───────────────────────────────────────────────────────────────
@admin_required
def custom_admin_dates(request):
    venue_filter = request.GET.get('venue', '')
    qs = DateEntry.objects.all().order_by('date')
    if venue_filter:
        qs = qs.filter(venue=venue_filter)
    return render(request, 'testproj/custom-admin/dates.html', {
        'dates':         qs,
        'venue_filter':  venue_filter,
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_add_date(request):
    if request.method == 'POST':
        venue    = request.POST.get('venue', 'birthday')
        date_val = request.POST.get('date')
        DateEntry.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={
                'status':     request.POST.get('status', 'booked'),
                'event_name': request.POST.get('event_name', '').strip(),
                'pax':        request.POST.get('pax') or None,
                'time_slot':  request.POST.get('time_slot', '').strip(),
            }
        )
        messages.success(request, f'Date {date_val} added.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/add_date.html', {
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_edit_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        entry.venue      = request.POST.get('venue', entry.venue)
        entry.date       = request.POST.get('date')
        entry.status     = request.POST.get('status', 'booked')
        entry.event_name = request.POST.get('event_name', '').strip()
        entry.pax        = request.POST.get('pax') or None
        entry.time_slot  = request.POST.get('time_slot', '').strip()
        entry.save()
        messages.success(request, f'Date {entry.date} updated.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/edit_date.html', {
        'entry':         entry,
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        label = str(entry.date)
        entry.delete()
        messages.success(request, f'Date {label} deleted.')
    return redirect('custom_admin_dates')

# ── ADMIN INQUIRIES ───────────────────────────────────────────────────────────
@admin_required
def custom_admin_inquiries(request):
    venue_filter = request.GET.get('venue', '')
    qs = BookingInquiry.objects.all()
    if venue_filter:
        qs = qs.filter(venue=venue_filter)
    qs.filter(is_read=False).update(is_read=True)
    return render(request, 'testproj/custom-admin/inquiries.html', {
        'inquiries':     qs.order_by('-submitted_at'),
        'venue_filter':  venue_filter,
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': 0,
    })

@admin_required
def custom_admin_approve_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirmed':
            inquiry.status = 'confirmed'
            DateEntry.objects.update_or_create(
                venue=inquiry.venue, date=inquiry.date,
                defaults={
                    'status':     'booked',
                    'event_name': inquiry.event_name,
                    'pax':        inquiry.pax,
                    'time_slot':  inquiry.time_slot,
                },
            )
            messages.success(request, f'Booking confirmed! {inquiry.date} is now locked.')
        elif action == 'declined':
            inquiry.status = 'declined'
            DateEntry.objects.filter(
                venue=inquiry.venue, date=inquiry.date
            ).delete()
            messages.success(request, f'Inquiry declined. {inquiry.date} is available again.')
        inquiry.save()
    return redirect('custom_admin_inquiries')

@admin_required
def custom_admin_bookings(request):
    return redirect('custom_admin_inquiries')

# ── ADMIN CALENDAR ────────────────────────────────────────────────────────────
@admin_required
def custom_admin_calendar(request):
    dates = DateEntry.objects.all()
    events_data = []
    for d in dates:
        events_data.append({
            'date':       d.date.isoformat(),
            'status':     d.status,
            'venue':      VENUE_NAMES.get(d.venue, d.venue),
            'event_name': d.event_name or 'Available',
        })
    return render(request, 'testproj/custom-admin/admin_calendar.html', {
        'events_json': json.dumps(events_data)
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