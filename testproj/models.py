from django.db import models
from django.utils import timezone


# ── Date Entry / Booking Table ──
class DateEntry(models.Model):
    VENUE_CHOICES = [
        ('birthday',      'Birthday & Private Venue'),
        ('wedding',       'Wedding & Romantic Venue'),
        ('family',        'Family Milestones Venue'),
        ('academic',      'Academic & Youth Venue'),
        ('corporate',     'Corporate & Formal Venue'),
        ('entertainment', 'Entertainment & Special Venue'),
    ]

    STATUS_CHOICES = [
        ('available',   'Available'),
        ('booked',      'Booked'),
        ('ongoing',     'Ongoing'),
        ('done',        'Done'),
        ('canceled',    'Canceled'),
        ('rescheduled', 'Rescheduled'),
        ('unavailable', 'Unavailable'),
    ]

    venue      = models.CharField(max_length=50, choices=VENUE_CHOICES, default='birthday')
    date       = models.DateField()
    event_name = models.CharField(max_length=255, blank=True, null=True)
    pax        = models.IntegerField(blank=True, null=True)
    time_slot  = models.CharField(max_length=100, blank=True, null=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    email      = models.EmailField(blank=True, null=True)
    notes      = models.TextField(blank=True, null=True)

    old_date          = models.DateField(null=True, blank=True)
    reschedule_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.venue} ({self.status})"


# ── Booking Inquiry ──
class BookingInquiry(models.Model):
    VENUE_CHOICES = DateEntry.VENUE_CHOICES

    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
    ]

    venue      = models.CharField(max_length=30, choices=VENUE_CHOICES, default='birthday')
    date       = models.DateField()
    name       = models.CharField(max_length=200)
    email      = models.EmailField()
    event_name = models.CharField(max_length=200, blank=True)
    pax        = models.IntegerField(null=True, blank=True)
    time_slot  = models.CharField(max_length=100, blank=True)
    notes      = models.TextField(blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.venue}] {self.name} — {self.date} ({self.status})"


# ── Booking Log ──
class BookingLog(models.Model):
    entry      = models.ForeignKey(DateEntry, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    status     = models.CharField(max_length=20, blank=True)
    note       = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry} → {self.status} at {self.changed_at}"


# ── Notes Log ──
class NotesLog(models.Model):
    note       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note at {self.created_at}"