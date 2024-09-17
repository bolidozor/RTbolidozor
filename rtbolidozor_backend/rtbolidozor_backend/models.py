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
    last_active = models.DateTimeField(default='2000-01-01 00:00:00')

    def __str__(self):
        return f"Station {self.identifier} - {self.name}"
    
    def get_absolute_url(self):
        return f"/o/{self.observatory.identifier}/{self.identifier}/"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['identifier', 'observatory'], name='unique_station')
        ]

class File(UUIDMixin):
    name = models.CharField(max_length=255)
    hash = models.CharField(max_length=255)
    file_path = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    server = models.CharField(max_length=255, null=True, blank=True)
    online = models.BooleanField(default=True)
    indexed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
    
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['file_path'], name='unique_file')
    #     ]


# class EventMetadata(UUIDMixin):
#     peak_frequency = models.FloatField()
#     magnitude = models.FloatField()
#     duration = models.FloatField(help_text="Duration of the event in seconds")
#     corrected_time_flag = models.BooleanField(default=False, help_text="Flag indicating if the time is corrected")
#     corrected_start_time = models.DateTimeField(help_text="Corrected start time of the event")


#     def __str__(self):
#         return f"Metadata for Event"
    
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['event'], name='unique_event_metadata')
#         ]


class Snapshot(UUIDMixin):
    snap_file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='snapshot', null=True, blank=True)
    station = models.ForeignKey('Station', on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField("Snapshot timestamp, start of the observation", null=True, blank=True)
    duration = models.FloatField(help_text="Duration of the snapshot in seconds", null=True, blank=True)


class Event(UUIDMixin):
    met_file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='event_met', null=True, blank=True)
    raw_file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='event_raw', null=True, blank=True)
    obs_start_time = models.DateTimeField(help_text="System start time of the event")
    station = models.ForeignKey('Station', on_delete=models.CASCADE, related_name='events')
    #metadata = models.OneToOneField('EventMetadata', on_delete=models.CASCADE, related_name='event', null=True, blank=True)
    peak_frequency = models.FloatField(null=True)
    magnitude = models.FloatField(null=True)
    duration = models.FloatField(null=True, help_text="Duration of the event in seconds")
    corrected_time_flag = models.BooleanField(null=True, default=False, help_text="Flag indicating if the time is corrected")
    corrected_start_time = models.DateTimeField(null=True, help_text="Corrected start time of the event")


    def __str__(self):
        return f"Event at {self.exact_start_time} from {self.station}"
    
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['obs_start_time', 'station'], name='unique_event')
    #     ]

class MultiStationEvent(UUIDMixin):
    timestamp = models.DateTimeField()
    events = models.ManyToManyField('Event', related_name='other_stations')

    def __str__(self):
        return f"MultiStationEvent at {self.timestamp}"
    