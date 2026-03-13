from django.db import models

class BookedDate(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('unavailable', 'Unavailable'),
        ('available', 'Available'),
    ]
    date       = models.DateField()
    event_name = models.CharField(max_length=200, blank=True)
    pax        = models.IntegerField(null=True, blank=True)
    time_slot  = models.CharField(max_length=100, blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    def __str__(self):
        return f"{self.event_name} - {self.date}"


class BookingInquiry(models.Model):
    date         = models.DateField()
    name         = models.CharField(max_length=200)
    email        = models.EmailField()
    event_name   = models.CharField(max_length=200)
    pax          = models.IntegerField(null=True, blank=True)
    time_slot    = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(
        max_length=20,
        choices=[('pending','Pending'),('confirmed','Confirmed'),('declined','Declined')],
        default='pending'
    )

    def __str__(self):
        return f"{self.name} — {self.date}"

    class Meta:
        ordering = ['date']

class Booking(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    event_name = models.CharField(max_length=200)
    pax = models.IntegerField(null=True, blank=True)
    time_slot = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)