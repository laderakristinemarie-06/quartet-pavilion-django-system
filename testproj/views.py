from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from datetime import date
from django.utils import timezone
from testproj.models import BookedDate, Booking, BookingInquiry
import json


def home(request):
    return render(request, 'testproj/home.html')

def events(request):
    return render(request, 'testproj/events.html')

def overview(request):
    return render(request, 'testproj/overview.html')

def gallery(request):
    return render(request, 'testproj/gallery.html')

def room(request):
    return render(request, 'testproj/room.html')

def testimonials(request):
    return render(request, 'testproj/testimonials.html')

def book(request):
    return render(request, 'testproj/book.html')

def log_in(request):
    return render(request, 'testproj/log_in.html')

def admin_required(view_func):
    """Simple decorator to protect custom admin     views."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────
def custom_admin_login(request):
    if request.session.get('is_admin'):
        return redirect('custom_admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            request.session['is_admin'] = True
            request.session['admin_username'] = user.username
            return redirect('custom_admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'testproj/custom-admin/login.html')


def custom_admin_logout(request):
    request.session.flush()
    return redirect('custom_admin_login')


def custom_admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('custom_admin_login')
    
    now = timezone.now()
    booked_count = BookedDate.objects.filter(status='booked').count()
    unavailable_count = BookedDate.objects.filter(status='unavailable').count()
    upcoming = BookedDate.objects.filter(date__gte=now.date()).order_by('date')[:10]
    
    # Add bookings/inquiries
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    new_bookings = Booking.objects.filter(is_read=False).count()

    return render(request, 'testproj/custom-admin/dashboard.html', {
        'booked_count': booked_count,
        'unavailable_count': unavailable_count,
        'upcoming': upcoming,
        'recent_bookings': recent_bookings,
        'new_bookings': new_bookings,
    })

# ─────────────────────────────────────────────
#  MANAGE DATES
# ─────────────────────────────────────────────
@admin_required
def custom_admin_dates(request):
    dates = BookedDate.objects.all().order_by('date')
    return render(request, 'testproj/custom-admin/dates.html', {'dates': dates})


# ─────────────────────────────────────────────
#  ADD DATE
# ─────────────────────────────────────────────
@admin_required
def custom_admin_add_date(request):
    if request.method == 'POST':
        date_val   = request.POST.get('date')
        status     = request.POST.get('status', 'booked')
        event_name = request.POST.get('event_name', '').strip()
        pax        = request.POST.get('pax') or None
        time_slot  = request.POST.get('time_slot', '').strip()

        BookedDate.objects.create(
            date=date_val,
            status=status,
            event_name=event_name,
            pax=pax,
            time_slot=time_slot,
        )
        messages.success(request, f'Date {date_val} has been added successfully.')
        return redirect('custom_admin_dates')

    return render(request, 'testproj/custom-admin/add_date.html')


# ─────────────────────────────────────────────
#  EDIT DATE
# ─────────────────────────────────────────────
@admin_required
def custom_admin_edit_date(request, pk):
    entry = get_object_or_404(BookedDate, pk=pk)

    if request.method == 'POST':
        entry.date       = request.POST.get('date')
        entry.status     = request.POST.get('status', 'booked')
        entry.event_name = request.POST.get('event_name', '').strip()
        entry.pax        = request.POST.get('pax') or None
        entry.time_slot  = request.POST.get('time_slot', '').strip()
        entry.save()

        messages.success(request, f'Date {entry.date} has been updated successfully.')
        return redirect('custom_admin_dates')

    return render(request, 'testproj/custom-admin/edit_date.html', {'entry': entry})


# ─────────────────────────────────────────────
#  DELETE DATE
# ─────────────────────────────────────────────
@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(BookedDate, pk=pk)

    if request.method == 'POST':
        date_label = str(entry.date)
        entry.delete()
        messages.success(request, f'Date {date_label} has been deleted.')
        return redirect('custom_admin_dates')

    # If accessed via GET, redirect safely
    return redirect('custom_admin_dates')

def calendar(request):
    booked_dates = BookedDate.objects.filter(status='booked').values('date', 'event_name', 'pax', 'time_slot')
    unavailable_dates = BookedDate.objects.filter(status='unavailable').values('date')

    context = {
        'booked_dates':      json.dumps(list(booked_dates),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable_dates), cls=DjangoJSONEncoder),
    }
    return render(request, 'testproj/calendar.html', context)

def submit_booking(request):
    if request.method == 'POST':
        Booking.objects.create(
            date=request.POST.get('date'),
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            event_name=request.POST.get('event_name'),
            pax=request.POST.get('pax') or None,
            time_slot=request.POST.get('time_slot'),
            notes=request.POST.get('notes'),
        )
        return redirect(f"{request.META.get('HTTP_REFERER', '/calendar/')}?success=1")
    return redirect('calendar')

@admin_required
def custom_admin_inquiries(request):
    inquiries = BookingInquiry.objects.all().order_by('date')
    return render(request, 'testproj/custom-admin/inquiries.html', {'inquiries': inquiries})

@admin_required
def custom_admin_dashboard(request):
    from datetime import date
    today = date.today()
 
    booked_count      = BookedDate.objects.filter(status='booked').count()
    unavailable_count = BookedDate.objects.filter(status='unavailable').count()
    pending_count     = BookingInquiry.objects.filter(status='pending').count()
    upcoming          = BookedDate.objects.filter(status='booked', date__gte=today).order_by('date')[:10]
    recent_inquiries  = BookingInquiry.objects.filter(status='pending').order_by('submitted_at')[:5]
 
    context = {
        'booked_count':      booked_count,
        'unavailable_count': unavailable_count,
        'pending_count':     pending_count,
        'upcoming':          upcoming,
        'recent_inquiries':  recent_inquiries,
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)

def custom_admin_bookings(request):
    if not request.session.get('is_admin'):
        return redirect('custom_admin_login')
    bookings = Booking.objects.all().order_by('-created_at')
    # Mark all as read when viewed
    Booking.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'testproj/custom-admin/bookings.html', {'bookings': bookings})