#!/bin/bash
# Spustí hledání multibolid detekcí (MeteorClusterer) za zadané období.
# Použití: ./run_multibolid_history.sh YYYY-MM-DD [YYYY-MM-DD]
# Příklad: ./run_multibolid_history.sh 2026-02-01
#          ./run_multibolid_history.sh 2026-02-01 2026-04-30
#
# Poznámka: Před spuštěním tohoto skriptu je doporučeno nejprve spustit
#           reindex_history.sh pro stejné období.

DATE_FROM="${1:?Chybi parametr date_from, napr. 2026-02-01}"
DATE_TO="${2:-$(date -u +%Y-%m-%d)}"

echo "Hledani multibolidu od $DATE_FROM do $DATE_TO"

docker exec django_q python3 -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtbolidozor_backend.settings')
django.setup()

from datetime import datetime, timezone
from rtbolidozor_backend.tasks import MeteorClusterer

date_from = datetime.strptime('$DATE_FROM', '%Y-%m-%d').replace(tzinfo=timezone.utc)
date_to   = datetime.strptime('$DATE_TO',   '%Y-%m-%d').replace(tzinfo=timezone.utc)

print('Spoustim MeteorClusterer od', date_from, 'do', date_to)
MeteorClusterer(date_from=date_from, date_to=date_to)
print('Hotovo.')
"
