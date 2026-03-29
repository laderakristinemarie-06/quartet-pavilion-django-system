from django.db import models

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
        ('pending',     'Pending'),
        ('booked',      'Booked'),
        ('ongoing',     'Ongoing'),
        ('done',        'Done'),
        ('unavailable', 'Unavailable'),
        ('rescheduled', 'Rescheduled'),
        ('canceled',    'Canceled'),
    ]

    venue      = models.CharField(max_length=50, choices=VENUE_CHOICES)
    date       = models.DateField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    event_name = models.CharField(max_length=255, blank=True, null=True)
    name       = models.CharField(max_length=100, blank=True, null=True)   # client name
    email      = models.EmailField(blank=True, null=True)
    pax        = models.IntegerField(blank=True, null=True)
    time_slot  = models.CharField(max_length=100, blank=True, null=True)
    notes      = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.venue} ({self.status})"


# ── Booking Inquiries ──
class BookingInquiry(models.Model):
    INQUIRY_STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('declined',  'Declined'),
    ]

    venue        = models.CharField(max_length=50)
    date         = models.DateField()
    name         = models.CharField(max_length=100)
    email        = models.EmailField()
    event_name   = models.CharField(max_length=200)
    pax          = models.IntegerField(null=True, blank=True)
    time_slot    = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)
    status       = models.CharField(
                       max_length=20,
                       choices=INQUIRY_STATUS_CHOICES,
                       default='pending'
                   )
    admin_notes  = models.TextField(blank=True, default='')   # ← internal admin notes
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read      = models.BooleanField(default=False)

    def get_venue_display_name(self):
        VENUE_NAMES = {
            'birthday':      'Birthday & Private Venue',
            'wedding':       'Wedding & Romantic Venue',
            'family':        'Family Milestones Venue',
            'academic':      'Academic & Youth Venue',
            'corporate':     'Corporate & Formal Venue',
            'entertainment': 'Entertainment & Special Venue',
        }
        return VENUE_NAMES.get(self.venue, self.venue.title())

    def __str__(self):
        return f"Inquiry from {self.name} for {self.date} ({self.status})"


# ── Logs ──
class BookingLog(models.Model):
    action    = models.CharField(max_length=255, default='', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class NotesLog(models.Model):
    note       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)