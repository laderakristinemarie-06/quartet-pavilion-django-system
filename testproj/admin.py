from django.contrib import admin
from .models import DateEntry, BookingInquiry, BookingLog, NotesLog

admin.site.register(DateEntry)
admin.site.register(BookingInquiry)
admin.site.register(BookingLog)
admin.site.register(NotesLog)