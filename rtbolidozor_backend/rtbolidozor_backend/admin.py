from django.contrib import admin
from .models import Station, Observatory, BolidozorUser, Event, File, MultiStationEvent

admin.site.register(Station)
admin.site.register(Observatory)
admin.site.register(BolidozorUser)
admin.site.register(Event)
admin.site.register(MultiStationEvent)
#admin.site.register(EventMetadata)

admin.site.register(File)