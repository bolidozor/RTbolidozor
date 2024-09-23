import os, sys
import pandas as pd
from datetime import datetime, timezone
import django
from django.utils.dateparse import parse_datetime
from astropy.io import fits


sys.path.append('../rtbolidozor_backend')
sys.path.append('../app')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rtbolidozor_backend.settings")
django.setup()

from rtbolidozor_backend.models import File, Event, Station, MultiStationEvent
from rtbolidozor_backend.tasks import find_multibolid, MeteorClusterer
import glob2

if __name__ == "__main__":


    # print("Mazani DB")
    # MultiStationEvent.objects.all().delete()
    # print("Mazani dokonceno")
    MeteorClusterer()
