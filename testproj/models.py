from django.db import models

# ── Date Entry / Booking Table ──
class DateEntry(models.Model):
    VENUE_CHOICES = [
        ('birthday', 'Birthday & Private Venue'),
        ('wedding', 'Wedding & Romantic Venue'),
        ('family', 'Family Milestones Venue'),
        ('academic', 'Academic & Youth Venue'),
        ('corporate', 'Corporate & Formal Venue'),
        ('entertainment', 'Entertainment & Special Venue'),
    ]

<<<<<<< HEAD
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
=======
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('unavailable', 'Unavailable'),
        ('rescheduled', 'Rescheduled'),
    ]
>>>>>>> 3f48afcb11aa28efde0d3401f0759da5cba8ae15

    venue = models.CharField(max_length=50, choices=VENUE_CHOICES)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # User Info
    event_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    pax = models.IntegerField(blank=True, null=True)
    time_slot = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.venue} ({self.status})"

<<<<<<< HEAD

# ── ADDED: BookingInquiry (was imported in views.py but missing from models) ──
class BookingInquiry(models.Model):
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


=======
# ── Booking Inquiries (For the Submit Form) ──
class BookingInquiry(models.Model):
    venue = models.CharField(max_length=50)
    date = models.DateField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    event_name = models.CharField(max_length=200)
    pax = models.IntegerField(null=True, blank=True)
    time_slot = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Inquiry from {self.name} for {self.date}"

# ── Logs ──
>>>>>>> 3f48afcb11aa28efde0d3401f0759da5cba8ae15
class BookingLog(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)


class NotesLog(models.Model):
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)