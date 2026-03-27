from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date
from testproj.models import BookedDate, BookingInquiry
import json

VENUE_NAMES = {
    'birthday':      'Birthday & Private Venue',
    'wedding':       'Wedding & Romantic Venue',
    'family':        'Family Milestones Venue',
    'academic':      'Academic & Youth Venue',
    'corporate':     'Corporate & Formal Venue',
    'entertainment': 'Entertainment & Special Venue',
}

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('custom_admin_login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

def _venue_calendar_context(venue_slug):
    booked = BookedDate.objects.filter(venue=venue_slug, status='booked').values('date','event_name','pax','time_slot')
    unavailable = BookedDate.objects.filter(venue=venue_slug, status='unavailable').values('date')
    return {
        'booked_dates':      json.dumps(list(booked),      cls=DjangoJSONEncoder),
        'unavailable_dates': json.dumps(list(unavailable), cls=DjangoJSONEncoder),
        'venue_slug':        venue_slug,
    }

def home(request):        return render(request, 'testproj/home.html')
def events(request):      return render(request, 'testproj/events.html')
def about(request):       return render(request, 'testproj/about.html')
def log_in(request):      return render(request, 'testproj/log_in.html')

def book(request):
    venue    = request.GET.get('venue', 'birthday')
    next_url = request.GET.get('next', '/')
    return render(request, 'testproj/book.html', {
        'venue':      venue,
        'venue_name': VENUE_NAMES.get(venue, 'Quartet Pavilion'),
        'next_url':   next_url,
    })

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

        inquiry = BookingInquiry.objects.create(
            venue=venue, date=date_val, name=name, email=email,
            event_name=event_name, pax=pax, time_slot=time_slot, notes=notes,
        )

        BookedDate.objects.update_or_create(
            venue=venue, date=date_val,
            defaults={'status':'booked','event_name':event_name,'pax':pax,'time_slot':time_slot},
        )

        ctx = {
            'inquiry': inquiry, 'name': name, 'email': email, 'phone': phone,
            'venue_name': VENUE_NAMES.get(venue, venue.title()),
            'event_name': event_name, 'date': date_val,
            'departure_date': departure_date, 'start_time': start_time, 'end_time': end_time,
            'pax': pax, 'time_slot': time_slot, 'payment': payment,
            'account_number': account_number, 'reference_number': reference_number,
            'total_price': total_price, 'downpay_amount': downpay_amount,
            'notes': notes, 'is_walkin': payment == 'walkin',
            'booking_id': f'QP-{inquiry.pk:05d}',
        }

        try:
            msg = EmailMultiAlternatives(
                subject=f'Booking Inquiry Received — Quartet Pavilion ({ctx["booking_id"]})',
                body=f'Hi {name}, your inquiry has been received. Booking ID: {ctx["booking_id"]}',
                from_email=settings.DEFAULT_FROM_EMAIL, to=[email],
            )
            msg.attach_alternative(render_to_string('testproj/emails/booking_client.html', ctx), 'text/html')
            msg.send(fail_silently=True)
        except Exception:
            pass

        try:
            msg2 = EmailMultiAlternatives(
                subject=f'New Booking — {name} | {VENUE_NAMES.get(venue,venue)} | {date_val}',
                body=f'New booking inquiry from {name} for {date_val}.',
                from_email=settings.DEFAULT_FROM_EMAIL, to=[settings.ADMIN_EMAIL],
            )
            msg2.attach_alternative(render_to_string('testproj/emails/booking_admin.html', ctx), 'text/html')
            msg2.send(fail_silently=True)
        except Exception:
            pass

        return redirect('booking_receipt', pk=inquiry.pk)

    return redirect('home')

def booking_receipt(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    return render(request, 'testproj/booking_receipt.html', {
        'inquiry':    inquiry,
        'venue_name': VENUE_NAMES.get(inquiry.venue, inquiry.venue.title()),
        'booking_id': f'QP-{inquiry.pk:05d}',
    })

def custom_admin_login(request):
    if request.session.get('is_admin'):
        return redirect('custom_admin_dashboard')
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        user = authenticate(request, username=request.POST.get('username','').strip(), password=request.POST.get('password',''))
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

@admin_required
def custom_admin_dashboard(request):
    today = date.today()
    context = {
        'booked_count':      BookedDate.objects.filter(status='booked').count(),
        'unavailable_count': BookedDate.objects.filter(status='unavailable').count(),
        'pending_count':     BookingInquiry.objects.filter(status='pending').count(),
        'new_inquiries':     BookingInquiry.objects.filter(is_read=False).count(),
        'upcoming':          BookedDate.objects.filter(status='booked', date__gte=today).order_by('date')[:10],
        'recent_inquiries':  BookingInquiry.objects.filter(status='pending').order_by('-submitted_at')[:5],
    }
    return render(request, 'testproj/custom-admin/dashboard.html', context)

@admin_required
def custom_admin_dates(request):
    from testproj.models import VENUE_CHOICES
    venue_filter = request.GET.get('venue', '')
    qs = BookedDate.objects.all().order_by('date')
    if venue_filter: qs = qs.filter(venue=venue_filter)
    return render(request, 'testproj/custom-admin/dates.html', {
        'dates': qs, 'venue_filter': venue_filter, 'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_add_date(request):
    from testproj.models import VENUE_CHOICES
    if request.method == 'POST':
        venue=request.POST.get('venue','birthday'); date_val=request.POST.get('date')
        BookedDate.objects.update_or_create(venue=venue, date=date_val, defaults={
            'status':request.POST.get('status','booked'),
            'event_name':request.POST.get('event_name','').strip(),
            'pax':request.POST.get('pax') or None,
            'time_slot':request.POST.get('time_slot','').strip(),
        })
        messages.success(request, f'Date {date_val} added.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/add_date.html', {
        'venue_choices': VENUE_CHOICES, 'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_edit_date(request, pk):
    from testproj.models import VENUE_CHOICES
    entry = get_object_or_404(BookedDate, pk=pk)
    if request.method == 'POST':
        entry.venue=request.POST.get('venue',entry.venue); entry.date=request.POST.get('date')
        entry.status=request.POST.get('status','booked'); entry.event_name=request.POST.get('event_name','').strip()
        entry.pax=request.POST.get('pax') or None; entry.time_slot=request.POST.get('time_slot','').strip()
        entry.save(); messages.success(request, f'Date {entry.date} updated.')
        return redirect('custom_admin_dates')
    return render(request, 'testproj/custom-admin/edit_date.html', {
        'entry': entry, 'venue_choices': VENUE_CHOICES,
        'new_inquiries': BookingInquiry.objects.filter(is_read=False).count(),
    })

@admin_required
def custom_admin_delete_date(request, pk):
    entry = get_object_or_404(BookedDate, pk=pk)
    if request.method == 'POST':
        label = str(entry.date); entry.delete()
        messages.success(request, f'Date {label} deleted.')
    return redirect('custom_admin_dates')

@admin_required
def custom_admin_inquiries(request):
    from testproj.models import VENUE_CHOICES
    venue_filter = request.GET.get('venue', '')
    qs = BookingInquiry.objects.all()
    if venue_filter: qs = qs.filter(venue=venue_filter)
    qs.filter(is_read=False).update(is_read=True)
    return render(request, 'testproj/custom-admin/inquiries.html', {
        'inquiries': qs.order_by('-submitted_at'), 'venue_filter': venue_filter,
        'venue_choices': VENUE_CHOICES, 'new_inquiries': 0,
    })

@admin_required
def custom_admin_approve_inquiry(request, pk):
    inquiry = get_object_or_404(BookingInquiry, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'confirmed':
            inquiry.status = 'confirmed'
            BookedDate.objects.update_or_create(
                venue=inquiry.venue, date=inquiry.date,
                defaults={'status':'booked','event_name':inquiry.event_name,'pax':inquiry.pax,'time_slot':inquiry.time_slot},
            )
            messages.success(request, f'Booking confirmed! {inquiry.date} is now locked.')
        elif action == 'declined':
            inquiry.status = 'declined'
            BookedDate.objects.filter(venue=inquiry.venue, date=inquiry.date).delete()
            messages.success(request, f'Inquiry declined. {inquiry.date} is available again.')
        inquiry.save()
    return redirect('custom_admin_inquiries')

@admin_required
def custom_admin_bookings(request):
    return redirect('custom_admin_inquiries')