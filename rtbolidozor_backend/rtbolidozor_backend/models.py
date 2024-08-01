from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid



class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key = True,
        default = uuid.uuid4,
        editable = False,
        unique = True
    )



class BolidozorUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def get_full_name(self) -> str:
        return super().get_full_name()



class Observatory(models.Model):
    identifier = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


    def get_stations(self):
        return self.stations.all()

    def __str__(self):
        return f"Observatory {self.identifier}"

    def get_absolute_url(self):
        return f"/o/{self.identifier}/"



class Station(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired'),
        ('pending', 'Pending'),
        ('error', 'Error'),
        ('replaced', 'Replaced'),
    ]

    identifier = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    observatory = models.ForeignKey(Observatory, on_delete=models.CASCADE, related_name='stations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Station {self.identifier} - {self.name}"
    
    def get_absolute_url(self):
        return f"/o/{self.observatory.identifier}/{self.identifier}/"
