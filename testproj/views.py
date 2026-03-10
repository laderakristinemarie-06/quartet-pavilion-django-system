from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import BookedDate, AdminUser
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

def calendar(request):
    booked_dates = BookedDate.objects.all()

    # Pass dates to JS as JSON
    booked = [str(b.date) for b in booked_dates if b.status == 'booked']
    unavailable = [str(b.date) for b in booked_dates if b.status == 'unavailable']

    # Upcoming events (booked dates that have an event name)
    upcoming = booked_dates.filter(
        status='booked',
        event_name__isnull=False
    ).exclude(event_name='').order_by('date')[:4]

    context = {
        'booked_json': json.dumps({'booked': booked, 'unavailable': unavailable}),
        'upcoming_events': upcoming,
    }
    return render(request, 'testproj/calendar.html', context)

def testimonials(request):
    return render(request, 'testproj/testimonials.html')

def book(request):
    return render(request, 'testproj/book.html')

def login(request):
    return render(request, 'testproj/log_in.html')

# ─── Custom Admin Login ───────────────────────────────────────
def custom_admin_login(request):
    if request.session.get('admin_logged_in'):
        return redirect('custom_admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            admin = AdminUser.objects.get(username=username)
            if admin.check_password(password):
                request.session['admin_logged_in'] = True
                request.session['admin_username'] = username
                return redirect('custom_admin_dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except AdminUser.DoesNotExist:
            messages.error(request, 'Admin user not found.')

    return render(request, 'testproj/custom-admin/login.html')


# ─── Custom Admin Logout ──────────────────────────────────────
def custom_admin_logout(request):
    request.session.flush()
    return redirect('custom_admin_login')


# ─── Admin Dashboard ──────────────────────────────────────────
def custom_admin_dashboard(request):
    if not request.session.get('admin_logged_in'):
        return redirect('custom_admin_login')

    booked_count = BookedDate.objects.filter(status='booked').count()
    unavailable_count = BookedDate.objects.filter(status='unavailable').count()
    upcoming = BookedDate.objects.filter(status='booked').order_by('date')[:5]

    context = {
        'booked_count': booked_count,
        'unavailable_count': unavailable_count,
        'upcoming': upcoming,
        'admin_username': request.session.get('admin_username'),
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)


# ─── Manage Dates (List) ──────────────────────────────────────
def custom_admin_dates(request):
    if not request.session.get('admin_logged_in'):
        return redirect('custom_admin_login')

    dates = BookedDate.objects.all().order_by('date')
    return render(request, 'testproj/custom-admin/dates.html', {'dates': dates})


# ─── Add Date ─────────────────────────────────────────────────
def custom_admin_add_date(request):
    if not request.session.get('admin_logged_in'):
        return redirect('custom_admin_login')

    if request.method == 'POST':
        date = request.POST.get('date')
        status = request.POST.get('status')
        event_name = request.POST.get('event_name', '')
        pax = request.POST.get('pax') or None
        time_slot = request.POST.get('time_slot', '')

        BookedDate.objects.create(
            date=date,
            status=status,
            event_name=event_name,
            pax=pax,
            time_slot=time_slot
        )
        messages.success(request, 'Date added successfully.')
        return redirect('custom_admin_dates')

    return render(request, 'testproj/custom-admin/add_date.html')


# ─── Edit Date ────────────────────────────────────────────────
def custom_admin_edit_date(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('custom_admin_login')

    entry = get_object_or_404(BookedDate, pk=pk)

    if request.method == 'POST':
        entry.date = request.POST.get('date')
        entry.status = request.POST.get('status')
        entry.event_name = request.POST.get('event_name', '')
        entry.pax = request.POST.get('pax') or None
        entry.time_slot = request.POST.get('time_slot', '')
        entry.save()
        messages.success(request, 'Date updated successfully.')
        return redirect('custom_admin_dates')

    return render(request, 'testproj/custom-admin/edit_date.html', {'entry': entry})


# ─── Delete Date ──────────────────────────────────────────────
def custom_admin_delete_date(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('custom_admin_login')

    entry = get_object_or_404(BookedDate, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Date deleted.')
    return redirect('custom_admin_dates')