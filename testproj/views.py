from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from testproj.models import BookedDate, BookingInquiry
import json

#Helpers
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def _venue_calendar_context(venue_slug):
    booked = BookedDate.objects.filter(
        venue=venue_slug, status='booked'
    ).values('date', 'event_name', 'pax', 'time_slot')

    unavailable = BookedDate.objects.filter(
        venue=venue_slug, status='unavailable'
    ).values('date')

    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'venue_slug':        venue_slug,
    }

#General
def home(request):
    return render(request, 'testproj/home.html')

def events(request):
    return render(request, 'testproj/events.html')

def about(request):
    return render(request, 'testproj/about.html')

def book(request):
    return render(request, 'testproj/book.html')

def log_in(request):
    return render(request, 'testproj/log_in.html')

#Birthday Venue
def birthday_overview(request):
    return render(request, 'testproj/birthday_overview.html')

def birthday_gallery(request):
    return render(request, 'testproj/birthday_gallery.html')

def birthday_room(request):
    return render(request, 'testproj/birthday_room.html')

def birthday_calendar(request):
    context = _venue_calendar_context('birthday')
    return render(request, 'testproj/birthday_calendar.html', context)

def birthday_testimonials(request):
    return render(request, 'testproj/birthday_testimonials.html')

#Wedding Venue
def wedding_overview(request):
    return render(request, 'testproj/wedding_overview.html')

def wedding_gallery(request):
    return render(request, 'testproj/wedding_gallery.html')

def wedding_room(request):
    return render(request, 'testproj/wedding_room.html')

def wedding_calendar(request):
    context = _venue_calendar_context('wedding')
    return render(request, 'testproj/wedding_calendar.html', context)

def wedding_testimonials(request):
    return render(request, 'testproj/wedding_testimonials.html')

#Family Milestones Venue
def family_overview(request):
    return render(request, 'testproj/family_overview.html')

def family_gallery(request):
    return render(request, 'testproj/family_gallery.html')

def family_room(request):
    return render(request, 'testproj/family_room.html')

def family_calendar(request):
    context = _venue_calendar_context('family')
    return render(request, 'testproj/family_calendar.html', context)

def family_testimonials(request):
    return render(request, 'testproj/family_testimonials.html')

#Academic & Youth Venue
def academic_overview(request):
    return render(request, 'testproj/academic_overview.html')

def academic_gallery(request):
    return render(request, 'testproj/academic_gallery.html')

def academic_room(request):
    return render(request, 'testproj/academic_room.html')

def academic_calendar(request):
    context = _venue_calendar_context('academic')
    return render(request, 'testproj/academic_calendar.html', context)

def academic_testimonials(request):
    return render(request, 'testproj/academic_testimonials.html')

#Corporate & Formal Venue
def corporate_overview(request):
    return render(request, 'testproj/corporate_overview.html')

def corporate_gallery(request):
    return render(request, 'testproj/corporate_gallery.html')

def corporate_room(request):
    return render(request, 'testproj/corporate_room.html')

def corporate_calendar(request):
    context = _venue_calendar_context('corporate')
    return render(request, 'testproj/corporate_calendar.html', context)

def corporate_testimonials(request):
    return render(request, 'testproj/corporate_testimonials.html')

#Entertainment & Special Venue
def entertainment_overview(request):
    return render(request, 'testproj/entertainment_overview.html')

def entertainment_gallery(request):
    return render(request, 'testproj/entertainment_gallery.html')

def entertainment_room(request):
    return render(request, 'testproj/entertainment_room.html')

def entertainment_calendar(request):
    context = _venue_calendar_context('entertainment')
    return render(request, 'testproj/entertainment_calendar.html', context)

def entertainment_testimonials(request):
    return render(request, 'testproj/entertainment_testimonials.html')

#Booking Submission
def submit_booking(request):
    if request.method == 'POST':
        venue      = request.POST.get('venue', 'birthday')
        date_val   = request.POST.get('date')
        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        event_name = request.POST.get('event_name', '').strip()
        pax        = request.POST.get('pax') or None
        time_slot  = request.POST.get('time_slot', '').strip()
        notes      = request.POST.get('notes', '').strip()

        BookingInquiry.objects.create(
            venue      = venue,
            date       = date_val,
            name       = name,
            email      = email,
            event_name = event_name,
            pax        = pax,
            time_slot  = time_slot,
            notes      = notes,
        )

        # Redirect back to the referrer with ?success=1 so the calendar
        # page shows the success message inside the modal.
        referer = request.META.get('HTTP_REFERER', '/')
        separator = '&' if '?' in referer else '?'
        return redirect(f"{referer}{separator}success=1")

    return redirect('home')

#Admin - Auth
def custom_admin_login(request):
    if request.session.get('is_admin'):
        return redirect('custom_admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            request.session['is_admin']        = True
            request.session['admin_username']  = user.username
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'testproj/custom-admin/login.html')


def custom_admin_logout(request):
    request.session.flush()
    return redirect('custom_admin_login')

#Admin Dashboard
@admin_required
def custom_admin_dashboard(request):
    today = date.today()

    booked_count      = BookedDate.objects.filter(status='booked').count()
    unavailable_count = BookedDate.objects.filter(status='unavailable').count()
    pending_count     = BookingInquiry.objects.filter(status='pending').count()
    new_inquiries     = BookingInquiry.objects.filter(is_read=False).count()

    # All upcoming booked dates across every venue
    upcoming = BookedDate.objects.filter(
        status='booked', date__gte=today
    ).order_by('date')[:10]

    # Most recent unread inquiries
    recent_inquiries = BookingInquiry.objects.filter(
        status='pending'
    ).order_by('-submitted_at')[:5]

    context = {
        'booked_count':      booked_count,
        'unavailable_count': unavailable_count,
        'pending_count':     pending_count,
        'new_inquiries':     new_inquiries,
        'upcoming':          upcoming,
        'recent_inquiries':  recent_inquiries,
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)

#Admin Manage Dates
@admin_required
def custom_admin_dates(request):
    from testproj.models import VENUE_CHOICES
    venue_filter = request.GET.get('venue', '')
    qs = BookedDate.objects.all().order_by('date')
    if venue_filter:
        qs = qs.filter(venue=venue_filter)

    return render(request, 'testproj/custom-admin/dates.html', {
        'dates':         qs,
        'venue_filter':  venue_filter,
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

#Admin - Add Dates
@admin_required
def custom_admin_add_date(request):
    from testproj.models import VENUE_CHOICES
    if request.method == 'POST':
        venue      = request.POST.get('venue', 'birthday')
        date_val   = request.POST.get('date')
        status     = request.POST.get('status', 'booked')
        event_name = request.POST.get('event_name', '').strip()
        pax        = request.POST.get('pax') or None
        time_slot  = request.POST.get('time_slot', '').strip()

        BookedDate.objects.update_or_create(
            venue = venue,
            date  = date_val,
            defaults={
                'status':     status,
                'event_name': event_name,
                'pax':        pax,
                'time_slot':  time_slot,
            },
        )
        messages.success(request, f'Date {date_val} added for {dict(VENUE_CHOICES)[venue]}.')
        return redirect('custom_admin_dates')

    return render(request, 'testproj/custom-admin/add_date.html', {
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

#Admin - Edit Date
@admin_required
def custom_admin_edit_date(request, pk):
    from testproj.models import VENUE_CHOICES
    entry = get_object_or_404(BookedDate, pk=pk)

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

#Admin - Delete Date
@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(BookedDate, pk=pk)
    if request.method == 'POST':
        label = str(entry.date)
        entry.delete()
        messages.success(request, f'Date {label} deleted.')
    return redirect('custom_admin_dates')

#Admin Inquiries
@admin_required
def custom_admin_inquiries(request):
    from testproj.models import VENUE_CHOICES
    venue_filter = request.GET.get('venue', '')
    qs = BookingInquiry.objects.all()
    if venue_filter:
        qs = qs.filter(venue=venue_filter)

    # Mark filtered (or all) inquiries as read when admin views them
    qs.filter(is_read=False).update(is_read=True)

    return render(request, 'testproj/custom-admin/inquiries.html', {
        'inquiries':     qs.order_by('-submitted_at'),
        'venue_filter':  venue_filter,
        'venue_choices': VENUE_CHOICES,
        'new_inquiries': 0,   # just marked them read
    })

#ADMIN — BOOKINGS (alias kept for backwards compat)
@admin_required
def custom_admin_bookings(request):
    return redirect('custom_admin_inquiries')