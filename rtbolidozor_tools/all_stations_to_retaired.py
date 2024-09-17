
import os
import django
import sys

sys.path.append('../rtbolidozor_backend')
sys.path.append('../app')

# Inicializace Django prostředí

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtbolidozor_backend.settings')
django.setup()
from rtbolidozor_backend.models import Station


Station.objects.all().update(status='retired')
