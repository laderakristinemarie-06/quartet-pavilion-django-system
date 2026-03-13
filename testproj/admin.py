from django.contrib import admin
from .models import BookedDate, Booking, BookingInquiry

@admin.register(BookedDate)
class BookedDateAdmin(admin.ModelAdmin):
    list_display  = ['date', 'event_name', 'pax', 'time_slot', 'status']
    list_filter   = ['status', 'date']
    search_fields = ['event_name']
    ordering      = ['date']
    list_editable = ['status']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event_name', 'date', 'pax', 'time_slot', 'created_at')
    list_filter = ('date', 'time_slot')
    search_fields = ('name', 'email', 'event_name')
    ordering = ('-created_at',)

@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event_name', 'date', 'pax', 'time_slot', 'status', 'submitted_at')
    list_filter = ('status', 'date')
    search_fields = ('name', 'email', 'event_name')
    ordering = ('-submitted_at',)