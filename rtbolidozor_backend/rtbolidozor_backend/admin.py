from django.contrib import admin
from .models import Station, Observatory, BolidozorUser

admin.site.register(Station)
admin.site.register(Observatory)
admin.site.register(BolidozorUser)