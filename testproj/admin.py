from django.contrib import admin
from .models import BookedDate

@admin.register(BookedDate)
class BookedDateAdmin(admin.ModelAdmin):
    list_display = ['date', 'status', 'event_name', 'pax', 'time_slot']
    list_filter = ['status']
    ordering = ['date']