from django.db import models
from django.utils import timezone

VENUE_CHOICES = [
    ('birthday',      'Birthday & Private Venue'),
    ('wedding',       'Wedding & Romantic Venue'),
    ('family',        'Family Milestones Venue'),
    ('academic',      'Academic & Youth Venue'),
    ('corporate',     'Corporate & Formal Venue'),
    ('entertainment', 'Entertainment & Special Venue'),
]

class DateEntry(models.Model):
    STATUS_CHOICES = [
        ('booked',      'Booked'),
        ('available',   'Available'),
        ('unavailable', 'Unavailable'),
        ('canceled',    'Canceled'),
        ('rescheduled', 'Rescheduled'),
        ('ongoing',     'Ongoing'),
        ('done',        'Done'),
    ]

    venue      = models.CharField(max_length=30, choices=VENUE_CHOICES, default='birthday')
    date       = models.DateField()
    event_name = models.CharField(max_length=200, blank=True)
    pax        = models.IntegerField(null=True, blank=True)
    time_slot  = models.CharField(max_length=100, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # REQUIRED FOR LOGIN - This must exist and be filled in the Admin
    email      = models.EmailField(blank=True, null=True)
    notes      = models.TextField(blank=True)
    
    old_date   = models.DateField(null=True, blank=True)
    reschedule_reason = models.TextField(blank=True)

    class Meta:
        ordering        = ['date']
        unique_together = ('venue', 'date')

    def __str__(self):
        return f"[{self.get_venue_display()}] {self.date} — {self.status}"

class BookingLog(models.Model):
    entry      = models.ForeignKey('DateEntry', on_delete=models.CASCADE, related_name='status_logs')
    status     = models.CharField(max_length=20)
    note       = models.TextField(blank=True, default='')
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['changed_at']

class NotesLog(models.Model):
    entry      = models.ForeignKey('DateEntry', on_delete=models.CASCADE, related_name='notes_logs')
    text       = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)