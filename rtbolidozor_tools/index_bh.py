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

from rtbolidozor_backend.models import File, Event, Station
from rtbolidozor_backend.tasks import file_index
import glob2

if __name__ == "__main__":
    #file_index(24*1, check_met=False, check_snap=False, check_meta=True)  # Data za poslední den
    file_index(date_from=datetime(2024, 1, 1), date_to=datetime(2024, 4, 1))  # Data v rozsahu
    print("Done")
