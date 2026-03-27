from django.contrib import admin
from .models import DateEntry, BookingLog, NotesLog

admin.site.register(DateEntry)
admin.site.register(BookingLog)
admin.site.register(NotesLog)