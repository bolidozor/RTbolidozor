"""
Doplní chybějící duration do Event záznamů z meta.csv souborů.
Zpracovává po měsících a stanicích, aby se nezdržovalo načítáním všeho najednou.

met.fits:  /storage/{obs}/{station}/meteors/{Y}/{M}/{D}/{H}/{filename}
meta.csv:  /storage/{obs}/{station}/data/{Y}/{M}/{D}/{YYYYMMDDH}0000_{station}_meta.csv
"""
import os, sys
import pandas as pd
from collections import defaultdict

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtbolidozor_backend.settings')

import django
django.setup()

from django.db.models import Min
from rtbolidozor_backend.models import Event


def met_path_to_meta_csv(path):
    parts = path.split('/')
    try:
        met_idx = parts.index('meteors')
    except ValueError:
        return None
    base    = '/'.join(parts[:met_idx])
    year    = parts[met_idx + 1]
    month   = parts[met_idx + 2]
    day     = parts[met_idx + 3]
    hour    = parts[met_idx + 4]
    fname   = parts[-1]
    station = fname.split('_')[1] if '_' in fname else ''
    meta_name = f"{year}{month}{day}{hour}0000_{station}_meta.csv"
    return f"{base}/data/{year}/{month}/{day}/{meta_name}"


def process_chunk(events_qs):
    """Zpracuje sadu eventů — seskupí dle meta.csv, doplní duration."""
    meta_map = defaultdict(list)
    for event in events_qs.iterator(chunk_size=2000):
        path = str(event.met_file.file_path)
        meta_path = met_path_to_meta_csv(path)
        if meta_path:
            meta_map[meta_path].append((event, path.split('/')[-1]))

    updated = skipped_nofile = skipped_notfound = 0

    for meta_path, ev_list in meta_map.items():
        if not os.path.exists(meta_path):
            skipped_nofile += len(ev_list)
            continue
        try:
            df = pd.read_csv(meta_path, sep=';', comment='#', header=0,
                             names=['filename', 'noise', 'peak_f', 'mag', 'duration'])
            df_met = df[df['filename'].str.contains('_met.fits', na=False)]
            dur_map = dict(zip(df_met['filename'], df_met['duration']))
        except Exception as e:
            print(f"    Chyba cteni {meta_path}: {e}")
            continue

        bulk = []
        for event, met_name in ev_list:
            if met_name in dur_map:
                event.duration = dur_map[met_name]
                bulk.append(event)
            else:
                skipped_notfound += 1

        if bulk:
            Event.objects.bulk_update(bulk, ['duration'], batch_size=500)
            updated += len(bulk)

    return updated, skipped_nofile, skipped_notfound


def backfill():
    base_qs = Event.objects.filter(
        duration__isnull=True,
        met_file__isnull=False
    ).select_related('met_file')

    total_missing = base_qs.count()
    print(f"Celkem eventu bez duration: {total_missing}")

    # Získej unikátní kombinace (stanice, rok, měsíc)
    combos = (
        base_qs
        .values('station_id', 'obs_start_time__year', 'obs_start_time__month')
        .distinct()
        .order_by('obs_start_time__year', 'obs_start_time__month', 'station_id')
    )
    combo_list = list(combos)
    print(f"Kombinaci (stanice × mesic): {len(combo_list)}\n")

    total_updated = total_nofile = total_notfound = 0

    for i, combo in enumerate(combo_list):
        station  = combo['station_id']
        year     = combo['obs_start_time__year']
        month    = combo['obs_start_time__month']

        chunk_qs = base_qs.filter(
            station_id=station,
            obs_start_time__year=year,
            obs_start_time__month=month,
        )
        count = chunk_qs.count()
        print(f"[{i+1}/{len(combo_list)}] {station} {year}/{month:02d} — {count} eventu", end=' ', flush=True)

        updated, nofile, notfound = process_chunk(chunk_qs)
        total_updated  += updated
        total_nofile   += nofile
        total_notfound += notfound
        print(f"→ doplneno: {updated}, bez CSV: {nofile}, nenalezeno v CSV: {notfound}")

    print(f"\n=== HOTOVO ===")
    print(f"  Doplneno celkem:        {total_updated}")
    print(f"  Meta.csv nenalezeno:    {total_nofile}")
    print(f"  Radek v CSV nenalezen:  {total_notfound}")


if __name__ == '__main__':
    backfill()
