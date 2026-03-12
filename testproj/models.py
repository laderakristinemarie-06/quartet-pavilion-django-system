from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class BookedDate(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('unavailable', 'Unavailable'),
    ]
    date        = models.DateField()
    event_name  = models.CharField(max_length=200, blank=True)
    pax         = models.IntegerField(null=True, blank=True)
    time_slot   = models.CharField(max_length=100, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')

    def __str__(self):
        return f"{self.event_name} - {self.date}"


class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username