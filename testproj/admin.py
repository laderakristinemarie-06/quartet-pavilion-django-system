from django.contrib import admin
from .models import BookedDate

@admin.register(BookedDate)
class BookedDateAdmin(admin.ModelAdmin):
    list_display  = ['date', 'event_name', 'pax', 'time_slot', 'status']
    list_filter   = ['status', 'date']
    search_fields = ['event_name']
    ordering      = ['date']
    list_editable = ['status']