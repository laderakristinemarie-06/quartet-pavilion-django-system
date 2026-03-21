from django.db import models


VENUE_CHOICES = [
    ('birthday',      'Birthday & Private Venue'),
    ('wedding',       'Wedding & Romantic Venue'),
    ('family',        'Family Milestones Venue'),
    ('academic',      'Academic & Youth Venue'),
    ('corporate',     'Corporate & Formal Venue'),
    ('entertainment', 'Entertainment & Special Venue'),
]


class BookedDate(models.Model):
    STATUS_CHOICES = [
        ('booked',      'Booked'),
        ('unavailable', 'Unavailable'),
        ('available',   'Available'),
    ]

    venue      = models.CharField(max_length=30, choices=VENUE_CHOICES, default='birthday')
    date       = models.DateField()
    event_name = models.CharField(max_length=200, blank=True)
    pax        = models.IntegerField(null=True, blank=True)
    time_slot  = models.CharField(max_length=100, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    class Meta:
        ordering        = ['date']
        # One status entry per venue per date — prevents accidental duplicates
        unique_together = ('venue', 'date')

    def __str__(self):
        return f"[{self.get_venue_display()}] {self.date} — {self.status}"


class BookingInquiry(models.Model):
    venue        = models.CharField(max_length=30, choices=VENUE_CHOICES, default='birthday')
    date         = models.DateField()
    name         = models.CharField(max_length=200)
    email        = models.EmailField()
    event_name   = models.CharField(max_length=200, blank=True)
    pax          = models.IntegerField(null=True, blank=True)
    time_slot    = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read      = models.BooleanField(default=False)
    status       = models.CharField(
        max_length=20,
        choices=[
            ('pending',   'Pending'),
            ('confirmed', 'Confirmed'),
            ('declined',  'Declined'),
        ],
        default='pending',
    )

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} — {self.get_venue_display()} — {self.date}"