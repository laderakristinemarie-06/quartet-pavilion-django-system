import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import send_mail
from django.conf import settings
from testproj.models import DateEntry, BookingInquiry

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
VENUE_NAMES = {
    'birthday':      'Birthday & Private Venue',
    'wedding':       'Wedding & Romantic Venue',
    'family':        'Family Milestones Venue',
    'academic':      'Academic & Youth Venue',
    'corporate':     'Corporate & Formal Venue',
    'entertainment': 'Entertainment & Special Venue',
}

VENUE_CHOICES = DateEntry.VENUE_CHOICES

# ── DECORATORS & HELPERS ──────────────────────────────────────────────────────
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _pending_count():
    """Helper: unread/pending inquiry count for sidebar badge."""
    return BookingInquiry.objects.filter(status='pending').count()


def _build_bookings_json(queryset):
    """
    Serialize a DateEntry queryset into the JSON shape expected by
    admin_calendar.html and user_calendar.html.
    """
    data = []
    for d in queryset:
        data.append({
            'id':          d.pk,
            'date':        d.date.isoformat(),
            'status':      d.status,
            'venue':       d.venue,
            'venue_label': d.get_venue_display() if hasattr(d, 'get_venue_display') else VENUE_NAMES.get(d.venue, d.venue),
            'event_name':  d.event_name or '',
            'name':        d.name or '',
            'pax':         d.pax or '',
            'time_slot':   d.time_slot or '',
            'notes':       d.notes or '',
        })
    return json.dumps(data, cls=DjangoJSONEncoder)


def _venue_calendar_context(venue_slug):
    """
    Context for public venue calendar pages.
    Only confirmed (booked) dates are shown as taken;
    pending shows as a "under review" indicator to clients.
    """
    booked = DateEntry.objects.filter(
        venue=venue_slug, status='booked'
    ).values('date', 'event_name', 'pax', 'time_slot')
    unavailable = DateEntry.objects.filter(
        venue=venue_slug, status='unavailable'
    ).values('date')
    pending = DateEntry.objects.filter(
        venue=venue_slug, status='pending'
    ).values('date')
    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'pending_dates':     json.dumps(list(pending),     cls=DjangoJSONEncoder),
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
            request.session['user_name']  = booking.name or ''
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

        # 1. Save inquiry (always pending until admin confirms)
        inquiry = BookingInquiry.objects.create(
            venue=venue, date=date_val, name=name, email=email,
            event_name=event_name, pax=pax, time_slot=time_slot,
            notes=notes, status='pending',
        )

        # 2. Mark date as PENDING on the calendar — not booked yet
        DateEntry.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={
                'status':     'pending',
                'event_name': event_name,
                'name':       name,
                'email':      email,
                'pax':        pax,
                'time_slot':  time_slot,
                'notes':      notes,
            },
        )

        booking_id = f'QP-{inquiry.pk:05d}'

        # 3. Email CLIENT — inquiry received
        try:
            send_mail(
                subject=f'Booking Inquiry Received — Quartet Pavilion ({booking_id})',
                message=f'''Hi {name},

Thank you for your interest in {VENUE_NAMES.get(venue, venue)}!

We have received your booking inquiry and our team will review it within 24 hours.
You will receive another email once your booking is confirmed or if we need more details.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOOKING INQUIRY DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID   : {booking_id}
Venue        : {VENUE_NAMES.get(venue, venue)}
Event        : {event_name}
Date         : {date_val}
Time         : {start_time} – {end_time}
Guests       : {pax} pax
Time Slot    : {time_slot}
Payment      : {payment.upper()}
Est. Total   : ₱{total_price}
Downpayment  : ₱{downpay_amount}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: PENDING — Awaiting admin confirmation

Please note: Your date is tentatively reserved but NOT yet confirmed.
Do not make any final arrangements until you receive your confirmation email.

Thank you for choosing Quartet Pavilion!
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Client email error: {e}")

        # 4. Email ADMIN — new inquiry alert
        try:
            send_mail(
                subject=f'⚠️ New Booking Inquiry — {name} | {VENUE_NAMES.get(venue, venue)} | {date_val}',
                message=f'''A new booking inquiry has been submitted and is waiting for your approval.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW BOOKING INQUIRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID   : {booking_id}
Status       : PENDING — Action Required

CLIENT INFO
Name         : {name}
Email        : {email}
Phone        : {phone}

RESERVATION
Venue        : {VENUE_NAMES.get(venue, venue)}
Event        : {event_name}
Date         : {date_val}
Time         : {start_time} – {end_time}
Guests       : {pax} pax
Time Slot    : {time_slot}

PAYMENT
Method       : {payment.upper()}
Reference #  : {reference_number}
Est. Total   : ₱{total_price}
Downpayment  : ₱{downpay_amount}

NOTES
{notes or 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please log in to the admin panel to CONFIRM or DECLINE this booking:
http://127.0.0.1:8000/manage/inquiries/
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Admin email error: {e}")

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
    today    = date.today()
    bookings = DateEntry.objects.filter(email=email)
    upcoming = bookings.filter(status__in=['booked', 'rescheduled'], date__gte=today).order_by('date')
    return render(request, 'testproj/user-panel/user_dashboard.html', {
        'bookings':         bookings,
        'total_bookings':   bookings.count(),
        'upcoming_count':   upcoming.count(),
        'ongoing_count':    bookings.filter(status='ongoing').count(),
        'done_count':       bookings.filter(status='done').count(),
        'upcoming_bookings': upcoming[:5],
    })

def user_bookings(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    status_filter = request.GET.get('status')
    bookings = DateEntry.objects.filter(email=email).order_by('date')
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
        'booking':   booking,
        'today_str': date.today().isoformat(),
    })

def user_calendar(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    bookings = DateEntry.objects.filter(email=email).order_by('date')
    data = []
    for b in bookings:
        data.append({
            'id':          b.pk,
            'date':        b.date.isoformat(),
            'status':      b.status,
            'venue':       b.venue,
            'venue_label': VENUE_NAMES.get(b.venue, b.venue),
            'event_name':  b.event_name or '',
            'pax':         b.pax,
            'time_slot':   b.time_slot or '',
            'detailUrl':   f'/my-account/bookings/{b.pk}/',
        })
    return render(request, 'testproj/user-panel/user_calendar.html', {
        'bookings_json': json.dumps(data, cls=DjangoJSONEncoder),
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
        'pending_count':     BookingInquiry.objects.filter(status='pending').count(),
        'unavailable_count': DateEntry.objects.filter(status='unavailable').count(),
        'new_bookings':      BookingInquiry.objects.filter(status='pending').count(),
        'upcoming':          DateEntry.objects.filter(
                                 status='booked', date__gte=today
                             ).order_by('date')[:10],
        'recent_bookings':   BookingInquiry.objects.filter(
                                 status='pending'
                             ).order_by('-submitted_at')[:5],
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)

# ── ADMIN DATES ───────────────────────────────────────────────────────────────
@admin_required
def custom_admin_dates(request):
    venue_filter  = request.GET.get('venue', '')
    status_filter = request.GET.get('status', '')
    qs = DateEntry.objects.all().order_by('date')
    if venue_filter:
        qs = qs.filter(venue=venue_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'testproj/custom-admin/dates.html', {
        'dates':          qs,
        'venue_filter':   venue_filter,
        'status_filter':  status_filter,
        'venue_choices':  VENUE_CHOICES,
        'status_choices': DateEntry.STATUS_CHOICES,
        'new_bookings':   _pending_count(),
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
                'name':       request.POST.get('name', '').strip(),
                'pax':        request.POST.get('pax') or None,
                'time_slot':  request.POST.get('time_slot', '').strip(),
                'notes':      request.POST.get('notes', '').strip(),
            }
        )
        messages.success(request, f'Date {date_val} added.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/add_date.html', {
        'venue_choices': VENUE_CHOICES,
        'new_bookings':  _pending_count(),
        'prefill_date':  request.GET.get('date', ''),
        'prefill_venue': request.GET.get('venue', ''),
    })

@admin_required
def custom_admin_edit_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        entry.venue      = request.POST.get('venue', entry.venue)
        entry.date       = request.POST.get('date', entry.date)
        entry.status     = request.POST.get('status', 'booked')
        entry.event_name = request.POST.get('event_name', '').strip()
        entry.name       = request.POST.get('name', '').strip()
        entry.pax        = request.POST.get('pax') or None
        entry.time_slot  = request.POST.get('time_slot', '').strip()
        entry.notes      = request.POST.get('notes', '').strip()
        entry.save()
        messages.success(request, f'Date {entry.date} updated.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/edit_date.html', {
        'entry':         entry,
        'venue_choices': VENUE_CHOICES,
        'new_bookings':  _pending_count(),
    })

@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(DateEntry, pk=pk)
    if request.method == 'POST':
        label = str(entry.date)
        entry.delete()
        messages.success(request, f'Date {label} deleted.')
    return redirect('custom_admin_dates')

# ── ADMIN INQUIRIES — LIST ────────────────────────────────────────────────────
@admin_required
def custom_admin_inquiries(request):
    venue_filter  = request.GET.get('venue', '')
    status_filter = request.GET.get('status', '')

    qs = BookingInquiry.objects.all()
    if venue_filter:
        qs = qs.filter(venue=venue_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Mark all fetched inquiries as read
    qs.filter(is_read=False).update(is_read=True)

    return render(request, 'testproj/custom-admin/inquiries.html', {
        'bookings':       qs.order_by('-submitted_at'),
        'venue_filter':   venue_filter,
        'status_filter':  status_filter,
        'venue_choices':  VENUE_CHOICES,
        'pending_count':  BookingInquiry.objects.filter(status='pending').count(),
        'accepted_count': BookingInquiry.objects.filter(status='confirmed').count(),
        'rejected_count': BookingInquiry.objects.filter(status='declined').count(),
        'new_bookings':   0,   # already read on this page
    })

# alias used by base_admin.html nav badge
@admin_required
def custom_admin_bookings(request):
    return redirect('custom_admin_inquiries')

# ── ADMIN INQUIRIES — CONFIRM (ACCEPT) ───────────────────────────────────────
@admin_required
def custom_admin_confirm_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        booking_id = f'QP-{inquiry.pk:05d}'

        # 1. Update inquiry status → confirmed
        inquiry.status  = 'confirmed'
        inquiry.is_read = True
        inquiry.save()

        # 2. Create/update DateEntry as 'booked' so it appears on the calendar
        DateEntry.objects.update_or_create(
            venue=inquiry.venue, date=inquiry.date,
            defaults={
                'status':     'booked',
                'event_name': inquiry.event_name,
                'name':       inquiry.name,
                'email':      inquiry.email,
                'pax':        inquiry.pax,
                'time_slot':  inquiry.time_slot,
                'notes':      inquiry.notes,
            },
        )

        # 3. Send CONFIRMATION email to client
        try:
            send_mail(
                subject=f'✅ Booking Confirmed! — Quartet Pavilion ({booking_id})',
                message=f'''Hi {inquiry.name},

Great news! Your booking has been CONFIRMED by our team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BOOKING CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID   : {booking_id}
Status       : ✅ CONFIRMED

Venue        : {VENUE_NAMES.get(inquiry.venue, inquiry.venue)}
Event        : {inquiry.event_name}
Date         : {inquiry.date}
Guests       : {inquiry.pax} pax
Time Slot    : {inquiry.time_slot}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your date is now officially reserved at Quartet Pavilion!

If you chose walk-in downpayment, please visit us at your earliest convenience:
Office hours: Monday – Saturday, 8:00 AM – 5:00 PM

For any questions, reply to this email or contact us directly.

We look forward to hosting your event!

Warm regards,
Quartet Pavilion Team
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Confirmation email error: {e}")

        messages.success(
            request,
            f'✅ Booking confirmed! {inquiry.name} on {inquiry.date} is now on the calendar.'
        )

    return redirect('custom_admin_inquiries')

# ── ADMIN INQUIRIES — DECLINE (REJECT) ───────────────────────────────────────
@admin_required
def custom_admin_decline_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        booking_id = f'QP-{inquiry.pk:05d}'

        # 1. Update inquiry status → declined
        inquiry.status  = 'declined'
        inquiry.is_read = True
        inquiry.save()

        # 2. Remove the pending DateEntry so the date opens back up
        DateEntry.objects.filter(
            venue=inquiry.venue, date=inquiry.date, status='pending'
        ).delete()

        # 3. Send DECLINE email to client
        try:
            send_mail(
                subject=f'Booking Update — Quartet Pavilion ({booking_id})',
                message=f'''Hi {inquiry.name},

Thank you for your interest in {VENUE_NAMES.get(inquiry.venue, inquiry.venue)}.

Unfortunately, we are unable to confirm your booking for {inquiry.date} at this time.
This may be due to the date no longer being available or other scheduling conflicts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID   : {booking_id}
Date         : {inquiry.date}
Status       : ❌ DECLINED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We encourage you to check our calendar for other available dates and submit a new inquiry.

We apologize for any inconvenience and hope to host your event soon!

Warm regards,
Quartet Pavilion Team
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inquiry.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Decline email error: {e}")

        messages.success(
            request,
            f'Inquiry from {inquiry.name} declined. {inquiry.date} is available again.'
        )

    return redirect('custom_admin_inquiries')

# ── ADMIN INQUIRIES — SAVE NOTE ───────────────────────────────────────────────
@admin_required
def custom_admin_inquiry_note(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        inquiry.admin_notes = request.POST.get('admin_notes', '').strip()
        inquiry.save()
        messages.success(request, 'Note saved.')
    return redirect('custom_admin_inquiries')

# ── ADMIN INQUIRIES — LEGACY COMBINED ACTION ──────────────────────────────────
@admin_required
def custom_admin_approve_inquiry(request, pk):
    """
    Legacy endpoint kept for backwards compatibility.
    Dispatches to confirm or decline based on POST 'action' field.
    """
    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'confirmed':
            return custom_admin_confirm_inquiry(request, pk)
        elif action == 'declined':
            return custom_admin_decline_inquiry(request, pk)
    return redirect('custom_admin_inquiries')

# ── ADMIN CALENDAR ────────────────────────────────────────────────────────────
@admin_required
def custom_admin_calendar(request):
    """
    All DateEntry records are shown on the admin calendar with colour-coded dots.
    Pending inquiry count still shows in the notice banner.
    """
    all_dates = DateEntry.objects.all().order_by('date')

    return render(request, 'testproj/custom-admin/admin_calendar.html', {
        'bookings_json': _build_bookings_json(all_dates),
        'pending_count': _pending_count(),
        'new_bookings':  _pending_count(),
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

# ── USER LOGOUT ───────────────────────────────────────────────────────────────
def user_logout(request):
    request.session.flush()
    return redirect('log_in')

# ── USER BOOKING RESCHEDULE ───────────────────────────────────────────────────
def user_booking_reschedule(request, pk):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)

    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        if new_date:
            old_date       = booking.date
            booking.date   = new_date
            booking.status = 'pending'   # back to pending until admin re-confirms
            booking.save()

            try:
                send_mail(
                    subject=f'Reschedule Request — {booking.event_name} | {booking.venue}',
                    message=f'''A client has requested to reschedule their booking.

Client  : {email}
Venue   : {VENUE_NAMES.get(booking.venue, booking.venue)}
Event   : {booking.event_name}
Old Date: {old_date}
New Date: {new_date}

Please review and confirm or decline in the admin panel:
http://127.0.0.1:8000/manage/inquiries/
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Reschedule email error: {e}")

            messages.success(request, f'Reschedule request submitted for {new_date}. Awaiting admin approval.')
            return redirect('user_bookings')

    return render(request, 'testproj/user-panel/user_reschedule.html', {
        'booking': booking
    })

# ── USER BOOKING CANCEL ───────────────────────────────────────────────────────
def user_booking_cancel(request, pk):
    email = request.session.get('user_email')
    if not email:
        return redirect('log_in')
    booking = get_object_or_404(DateEntry, pk=pk, email=email)

    if request.method == 'POST':
        venue_name     = VENUE_NAMES.get(booking.venue, booking.venue)
        cancelled_date = booking.date
        booking.delete()

        try:
            send_mail(
                subject=f'Booking Cancelled — {email} | {venue_name} | {cancelled_date}',
                message=f'''A client has cancelled their booking.

Client : {email}
Venue  : {venue_name}
Date   : {cancelled_date}

The date is now available again on the calendar.
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Cancel email error: {e}")

        try:
            send_mail(
                subject='Booking Cancellation Confirmed — Quartet Pavilion',
                message=f'''Hi,

Your booking has been successfully cancelled.

Venue : {venue_name}
Date  : {cancelled_date}

If you would like to rebook, please visit our website.

Regards,
Quartet Pavilion Team
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Cancel client email error: {e}")

        messages.success(request, 'Your booking has been cancelled successfully.')
        return redirect('user_bookings')

    return render(request, 'testproj/user-panel/user_cancel_confirm.html', {
        'booking': booking
    })