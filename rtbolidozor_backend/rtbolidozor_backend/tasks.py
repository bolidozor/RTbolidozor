
from django_q.tasks import async_task
import time 
from datetime import datetime, timedelta, timezone
import glob2
import re
import os
import hashlib
import pandas as pd

from .models import Snapshot, File, Event, Station, MultiStationEvent
from astropy.io import fits

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
           data = fh.read(8192)
           if not data:
               break
           m.update(data)
        return m.hexdigest()
    
def daterange(start_date, end_date):
    """Generátor pro iteraci přes dny."""
    for n in range(int((end_date - start_date).days) + 1):
        yield end_date - timedelta(n)
    

def generate_date_regex(year, month, day_start, day_end):
    """Vytvoří regex na základě roku, měsíce a rozsahu dnů."""
    day_range = f"[{day_start:02}-{day_end:02}]"
    return f"/{year}/{month:02}/{day_range}/"

        
def file_index(duration = None, date_from = None, date_to = None, check_met = True, check_snap = True, check_meta = True):
    start = datetime.now()

    if duration:
        time_end = datetime.now(timezone.utc)
        time_start = time_end - timedelta(hours=duration)
    elif date_from and date_to:
        time_start = date_from
        time_end = date_to
    else:
        raise ValueError("Either duration or date_from and date_to must be specified")


    for station_dir in glob2.glob('/storage/*/*'):
        print("Station dir: ", station_dir)
        station_name = station_dir.split('/')[-1]
        print("Station name: ", station_name)
        ostat = Station.objects.filter(identifier=station_name).first()
        if ostat: # and ostat.status == 'active':

            for date in daterange(time_start, time_end):
                search_path = f'{station_dir}/*/{date.year}/{date.month:02}/{date.day:02}/**'
                print("Searching in: ", search_path)

                new_ofiles = []
                new_osnaps = []
                for file in glob2.iglob(search_path):
                    try:
                        print(file)
                        name = file.split('/')[-1]
                        if 'snap' in file and '.fits' in name and check_snap:
                            if True:

                                #print("Name: ", name)
                                datetime_obj = datetime.strptime(name[0:17], "%Y%m%d%H%M%S%f").replace(tzinfo=timezone.utc)
                                #datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)

                                ofile = File.objects.filter(name=name).first()
                                if not ofile:
                                    #print("New file: ", file)
                                    ofile = File(file_path=file, name=name, hash=md5Checksum(file))
                                    ofile.save()
                                
                                try:
                                    osnap = ofile.snapshots
                                except Exception as e:
                                    osnap = Snapshot(snap_file=ofile, station_id=ostat.identifier, timestamp=datetime_obj, duration=60000)
                                    ofile.snapshots = osnap
                                
                                fits_header = fits.getheader(file, 1)
                                d = fits_header['DATE']
                                osnap.timestamp = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)                            
                                
                                osnap.save()

                                ofile.indexed = True
                                ofile.save()

                        if '_met.fits' in file and check_met:

                            datetime_obj = datetime.strptime(name[0:17], "%Y%m%d%H%M%S%f").replace(tzinfo=timezone.utc)

                            ofile = File.objects.filter(name=name).first()
                            rfile = File.objects.filter(name=name.replace('met.', 'raws.')).first()

                            print("Ofile", ofile)
                            if not ofile or not rfile:
                                print("New file: ", file)
                                ofile = File(file_path=file, name=name, hash=md5Checksum(file))
                                rfile = File(file_path=file.replace('met.', 'raws.'), name=name.replace('met.', 'raws.'), online=False)
                                ofile.save()
                                rfile.save()

                            try:
                                oevent = ofile.event_met
                            except Exception:
                                oevent = Event(met_file=ofile, raw_file=rfile, station_id=ostat.identifier, obs_start_time=datetime_obj)
                                ofile.event_met = oevent

                            fits_header = fits.getheader(file, 1)
                            d = fits_header['DATE']
                            oevent.obs_start_time = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                            for fits_key, attr in [('DURATION', 'duration'), ('PEAKFREQ', 'peak_frequency'), ('MAG', 'magnitude')]:
                                try:
                                    val = fits_header[fits_key]
                                    if val is not None and getattr(oevent, attr) is None:
                                        setattr(oevent, attr, float(val))
                                except KeyError:
                                    pass
                            oevent.save()

                            ofile.indexed = True
                            ofile.save()

                        if 'meta.csv' in file and check_meta:
                            print("Meta file: ", file)

                            file_hash = md5Checksum(file)
                            sfile, created = File.objects.update_or_create(name=name, defaults={'file_path': file, 'hash': file_hash, 'indexed': True, 'server': 'space'})
                            needs_to_parse = created or (sfile.hash != file_hash)
                            if needs_to_parse and not created:
                                sfile.hash = file_hash
                                sfile.save()

                            if needs_to_parse:
                                print("Parsing meta file: ", file)
                                df = pd.read_csv(file, sep=';', comment='#', header=0,
                                                 names=['filename', 'noise', 'peak_f', 'mag', 'duration'])
                                for _, row in df[df['filename'].str.contains('_met.fits', na=False)].iterrows():
                                    obj = File.objects.filter(name=row['filename']).first()
                                    if obj:
                                        try:
                                            try:
                                                oevent = obj.event_met
                                            except Exception:
                                                station_id = row['filename'].split('_')[1] if '_' in row['filename'] else ostat.identifier
                                                oevent = Event(met_file=obj, station_id=station_id, obs_start_time=datetime.now(timezone.utc))
                                                obj.event_met = oevent
                                                obj.save()
                                            oevent.peak_frequency = float(row['peak_f']) if pd.notna(row['peak_f']) else oevent.peak_frequency
                                            oevent.magnitude = float(row['mag']) if pd.notna(row['mag']) else oevent.magnitude
                                            oevent.duration = float(row['duration']) if pd.notna(row['duration']) else oevent.duration
                                            oevent.save()
                                        except Exception as e:
                                            print("Error metadata-met: ", e)

                                        




                    except Exception as e:
                        print("Error: ", e)
                        pass
        

    print("Task1 done: ", datetime.now() - start)
    return "Task1 done, duration {}".format(datetime.now() - start)


def updateStationStatus():
    start = datetime.now()
    metadata = {}
    for station in Station.objects.all():
        try:
            print("Station: ", station)
            metadata[station.identifier] = {
                'status_old': station.status,
            }

            last_event = station.events.order_by('-obs_start_time').first()
            last_snapshot = station.snapshot.order_by('-timestamp').first()

            metadata[station.identifier]['last_event'] = last_event
            metadata[station.identifier]['last_event_time'] = last_event.obs_start_time if last_event else None
            metadata[station.identifier]['last_snapshot'] = last_snapshot
            metadata[station.identifier]['last_snapshot_time'] = last_snapshot.timestamp if last_snapshot else None

            if station.status in ['active', 'inactive', 'offline', 'error']:

                if last_snapshot:
                    if last_snapshot.timestamp > datetime.now(timezone.utc) - timedelta(days=1):
                        station.status = 'active'
                    elif last_snapshot.timestamp > datetime.now(timezone.utc) - timedelta(days=7):
                        station.status = 'inactive'
                    else:
                        station.status = 'offline'
                else:
                    station.status = 'error'
            else:
                pass

            metadata[station.identifier]['status_new'] = station.status
            station.save()
        
        except Exception as e:
            print("Error: ", e)
            pass

    metadata['duration'] = datetime.now() - start

    print("StationStatusUpdate, duration: ", datetime.now() - start)
    return metadata


class MeteorClusterer:
    def __init__(self, min_duration_bolid=3, min_duration=1, max_offset=5, date_from=None, date_to=None):
        self.min_duration_bolid = min_duration_bolid
        self.min_duration = min_duration
        self.max_offset = timedelta(seconds=max_offset)
        self.cluster_time_tolerance = timedelta(seconds=8)
        self.date_from = date_from if date_from else datetime.now(timezone.utc) - timedelta(days=30)
        self.date_to = date_to if date_to else datetime.now(timezone.utc)

        self.run()
    

    def find_existing_cluster(self, event_time):
        # Hledá již existující klastr v podobném časovém okně
        return MultiStationEvent.objects.filter(
            timestamp__range=(event_time - self.cluster_time_tolerance, event_time + self.cluster_time_tolerance)
        ).first()

    def find_match(self):
        print("Minimalni delka bolidu je stanovena na", self.min_duration_bolid, "s. Minimalni delka derivatu je", self.min_duration, "s")
        print("Maximalni casova odchylka je", self.max_offset.seconds, "s")
        
        # Vyhledání všech událostí, které splňují kritéria
        events = Event.objects.filter(
            duration__gt=self.min_duration_bolid,
            obs_start_time__range=(self.date_from, self.date_to)
        ).order_by('-obs_start_time')[:200]

        for event in events:
            print(f"Mám vybranou událost: {event.id}, {event.obs_start_time}, {event.duration}")
            
            # Najít okolní události v časovém okně
            near_events = Event.objects.filter(
                obs_start_time__range=(event.obs_start_time - self.max_offset, event.obs_start_time + self.max_offset),
                #duration__gt=self.min_duration
            ).exclude(other_stations__isnull=False)[:20]

            if len(near_events) > 3:
                existing_cluster = self.find_existing_cluster(event.obs_start_time)

                if existing_cluster:
                    print(f"Existující klastr nalezen s ID {existing_cluster.id}, přidávám události.")
                    cluster = existing_cluster
                else:
                    # Vytvoření nového MultiStationEvent (klastru)
                    cluster_time = event.obs_start_time  # Nebo průměrný čas z událostí
                    cluster = MultiStationEvent.objects.create(timestamp=cluster_time)
                    print(f"Vytvořen nový MultiStationEvent s ID {cluster.id}.")

                # Přidání událostí do klastru
                for near_event in near_events:
                    cluster.events.add(near_event)
                
                print(f"Klastr s ID {cluster.id} obsahuje nyní {cluster.events.count()} událostí.")
     
                for event in near_events:
                    print(f" --- Událost {event.id}, {event.obs_start_time}, {event.duration}, {event.station}")

            else:
                print("Nalezeno méně než 3 události, nevytvářím klastr.")

    def run(self):
        self.find_match()


def find_multibolid():
    start = datetime.now()
    metadata = {}
    
    for event in Event.objects.filter(duration__gt=1):
        print("Event: ", event.obs_start_time, event.corrected_start_time, event.duration, event)


    
    metadata['duration'] = datetime.now() - start
    print("StationStatusUpdate, duration: ", datetime.now() - start)
    return metadata

# def spustit_uloha():
#     async_task('rtbolidozor_backend.tasks.file_index', 'param1', 'param2')

def run_meteor_clusterer():
    """Wrapper pro django-Q scheduler - spouští MeteorClusterer."""
    clusterer = MeteorClusterer()
    return f"MeteorClusterer dokoncen"


def generate_statistics():
    """Pre-generate statistics and cache them in CachedStats model."""
    from collections import defaultdict
    from django.db.models import Count, Avg, Min, Max
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, ExtractHour, ExtractWeek, ExtractYear, ExtractMonth
    from .models import CachedStats

    now = datetime.now(timezone.utc)
    year_ago       = now - timedelta(days=365)
    month_ago      = now - timedelta(days=30)
    five_years_ago = now - timedelta(days=365 * 5)

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _daily_series(qs, date_field='day'):
        result = {}
        for row in qs:
            key = row[date_field].strftime('%Y-%m-%d')
            sid = row.get('station__identifier', '__total__')
            result.setdefault(key, {})[sid] = row['count']
        return result

    def _monthly_series(qs, date_field='month'):
        result = {}
        for row in qs:
            key = row[date_field].strftime('%Y-%m')
            sid = row.get('station__identifier', '__total__')
            result.setdefault(key, {})[sid] = row['count']
        return result

    # ── Daily (last 365 days) ──────────────────────────────────────────────────
    daily_qs = (Event.objects
        .filter(obs_start_time__gte=year_ago)
        .annotate(day=TruncDay('obs_start_time'))
        .values('day', 'station__identifier')
        .annotate(count=Count('id'))
        .order_by('day'))
    daily_map = _daily_series(daily_qs)

    all_days = [(year_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(366)]
    stations_daily = sorted({sid for d in daily_map.values() for sid in d})
    daily_total = [sum(daily_map.get(d, {}).values()) for d in all_days]
    daily_by_station = {s: [daily_map.get(d, {}).get(s, 0) for d in all_days] for s in stations_daily}

    # ── Weekly (last 5 years) ──────────────────────────────────────────────────
    weekly_qs = (Event.objects
        .filter(obs_start_time__gte=five_years_ago)
        .annotate(week=TruncWeek('obs_start_time'))
        .values('week', 'station__identifier')
        .annotate(count=Count('id'))
        .order_by('week'))

    weekly_map = {}
    for row in weekly_qs:
        key = row['week'].strftime('%Y-%m-%d')
        weekly_map.setdefault(key, {})[row['station__identifier']] = row['count']

    all_weeks = []
    cur_week = five_years_ago - timedelta(days=five_years_ago.weekday())
    while cur_week <= now:
        all_weeks.append(cur_week.strftime('%Y-%m-%d'))
        cur_week += timedelta(weeks=1)

    stations_weekly = sorted({sid for w in weekly_map.values() for sid in w})
    weekly_total = [sum(weekly_map.get(w, {}).values()) for w in all_weeks]
    weekly_by_station = {s: [weekly_map.get(w, {}).get(s, 0) for w in all_weeks] for s in stations_weekly}

    # ── Monthly all-time ───────────────────────────────────────────────────────
    monthly_all_qs = (Event.objects
        .annotate(month=TruncMonth('obs_start_time'))
        .values('month', 'station__identifier')
        .annotate(count=Count('id'))
        .order_by('month'))
    monthly_map = _monthly_series(monthly_all_qs)

    first_month = Event.objects.aggregate(mn=Min('obs_start_time'))['mn']
    all_months = []
    if first_month:
        cur = first_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        while cur <= now:
            all_months.append(cur.strftime('%Y-%m'))
            cur = cur.replace(year=cur.year + 1, month=1) if cur.month == 12 else cur.replace(month=cur.month + 1)

    stations_monthly = sorted({sid for d in monthly_map.values() for sid in d})
    monthly_total = [sum(monthly_map.get(m, {}).values()) for m in all_months]
    monthly_by_station = {s: [monthly_map.get(m, {}).get(s, 0) for m in all_months] for s in stations_monthly}

    # ── Annual profile: normalized monthly + weekly patterns ──────────────────
    # For each year: normalize monthly/weekly totals to % of that year's events.
    # Average across all years → removes bias from year-to-year network growth.
    year_month_qs = (Event.objects
        .annotate(yr=ExtractYear('obs_start_time'), mo=ExtractMonth('obs_start_time'))
        .values('yr', 'mo')
        .annotate(count=Count('id')))

    year_week_qs = (Event.objects
        .annotate(yr=ExtractYear('obs_start_time'), wk=ExtractWeek('obs_start_time'))
        .values('yr', 'wk')
        .annotate(count=Count('id')))

    year_month_map = defaultdict(lambda: [0] * 12)
    for row in year_month_qs:
        year_month_map[row['yr']][row['mo'] - 1] = row['count']

    year_week_map = defaultdict(lambda: [0] * 53)
    for row in year_week_qs:
        year_week_map[row['yr']][row['wk']] = row['count']

    monthly_profiles, weekly_profiles = [], []
    monthly_abs_acc, weekly_abs_acc = [0] * 12, [0] * 52
    for yr, counts in year_month_map.items():
        total = sum(counts)
        if total >= 100:
            monthly_profiles.append([c / total * 100 for c in counts])
            for i in range(12):
                monthly_abs_acc[i] += counts[i]
    for yr, counts in year_week_map.items():
        total = sum(counts[1:53])
        if total >= 100:
            weekly_profiles.append([counts[w] / total * 100 for w in range(1, 53)])
            for i in range(52):
                weekly_abs_acc[i] += counts[i + 1]

    n_m = len(monthly_profiles) or 1
    n_w = len(weekly_profiles) or 1

    annual_monthly_norm = (
        [round(sum(p[i] for p in monthly_profiles) / n_m, 3) for i in range(12)]
        if monthly_profiles else [0.0] * 12
    )
    annual_weekly_norm = (
        [round(sum(p[i] for p in weekly_profiles) / n_w, 3) for i in range(52)]
        if weekly_profiles else [0.0] * 52
    )
    annual_monthly_abs = [round(monthly_abs_acc[i] / n_m, 1) for i in range(12)]
    annual_weekly_abs  = [round(weekly_abs_acc[i]  / n_w, 1) for i in range(52)]

    # ── Active stations by period ──────────────────────────────────────────────
    active_stations_5year = Event.objects.filter(obs_start_time__gte=five_years_ago).values('station').distinct().count()
    active_stations_year  = Event.objects.filter(obs_start_time__gte=year_ago).values('station').distinct().count()
    active_stations_month = Event.objects.filter(obs_start_time__gte=month_ago).values('station').distinct().count()

    # ── Hourly profile ─────────────────────────────────────────────────────────
    def _hourly_profile(since):
        qs = (Event.objects
            .filter(obs_start_time__gte=since)
            .annotate(hour=ExtractHour('obs_start_time'))
            .values('hour', 'station__identifier')
            .annotate(count=Count('id'))
            .order_by('hour'))
        by_station = {}
        total = [0] * 24
        for row in qs:
            h = int(row['hour'])
            s = row['station__identifier']
            total[h] += row['count']
            by_station.setdefault(s, [0] * 24)
            by_station[s][h] += row['count']
        return {'total': total, 'by_station': by_station}

    hourly_year  = _hourly_profile(year_ago)
    hourly_month = _hourly_profile(month_ago)

    # ── Station totals ─────────────────────────────────────────────────────────
    station_qs = (Event.objects
        .values('station__identifier', 'station__name')
        .annotate(count=Count('id'), avg_duration=Avg('duration'))
        .order_by('-count'))

    multibolid_counts = {}
    for mse in MultiStationEvent.objects.prefetch_related('events__station'):
        for ev in mse.events.all():
            sid = ev.station.identifier
            multibolid_counts[sid] = multibolid_counts.get(sid, 0) + 1

    station_totals = [
        {
            'station': row['station__identifier'],
            'name': row['station__name'],
            'count': row['count'],
            'avg_duration': round(row['avg_duration'], 3) if row['avg_duration'] else None,
            'multibolid_count': multibolid_counts.get(row['station__identifier'], 0),
        }
        for row in station_qs
    ]

    # ── Duration histogram ─────────────────────────────────────────────────────
    durations = list(Event.objects.filter(duration__isnull=False, duration__gt=0, duration__lte=10)
                     .values_list('duration', flat=True))
    dur_bins = [round(i * 0.5, 1) for i in range(21)]
    dur_counts = [0] * 20
    for d in durations:
        idx = min(int(d / 0.5), 19)
        dur_counts[idx] += 1
    dur_labels = [f'{dur_bins[i]}-{dur_bins[i+1]}s' for i in range(20)]

    # ── Frequency histogram ────────────────────────────────────────────────────
    freqs = list(Event.objects.filter(peak_frequency__isnull=False, peak_frequency__gt=0)
                 .values_list('peak_frequency', flat=True))
    if freqs:
        fmin, fmax = min(freqs), max(freqs)
        frange = fmax - fmin or 1
        fstep = frange / 20
        freq_bins = [round(fmin + i * fstep, 1) for i in range(21)]
        freq_counts = [0] * 20
        for f in freqs:
            idx = min(int((f - fmin) / fstep), 19)
            freq_counts[idx] += 1
        freq_labels = [f'{freq_bins[i]:.0f}-{freq_bins[i+1]:.0f}Hz' for i in range(20)]
    else:
        freq_labels, freq_counts = [], []

    # ── Summary ────────────────────────────────────────────────────────────────
    total_events = Event.objects.count()
    total_multibolid = MultiStationEvent.objects.count()
    active_stations = Station.objects.filter(status='active').count()
    agg = Event.objects.filter(duration__isnull=False).aggregate(avg=Avg('duration'), mn=Min('obs_start_time'), mx=Max('obs_start_time'))

    data = {
        'generated_at': now.isoformat(),
        'summary': {
            'total_events': total_events,
            'total_multibolid': total_multibolid,
            'active_stations_5year': active_stations_5year,
            'active_stations_year': active_stations_year,
            'active_stations_month': active_stations_month,
            'avg_duration': round(agg['avg'], 3) if agg['avg'] else None,
            'date_from': agg['mn'].isoformat() if agg['mn'] else None,
            'date_to': agg['mx'].isoformat() if agg['mx'] else None,
        },
        'daily': {
            'dates': all_days,
            'total': daily_total,
            'by_station': daily_by_station,
            'stations': stations_daily,
        },
        'weekly_5y': {
            'weeks': all_weeks,
            'total': weekly_total,
            'by_station': weekly_by_station,
            'stations': stations_weekly,
        },
        'monthly_all': {
            'months': all_months,
            'total': monthly_total,
            'by_station': monthly_by_station,
            'stations': stations_monthly,
        },
        'annual_profile': {
            'monthly_norm': annual_monthly_norm,
            'weekly_norm':  annual_weekly_norm,
            'monthly_abs':  annual_monthly_abs,
            'weekly_abs':   annual_weekly_abs,
            'n_years': len(monthly_profiles),
        },
        'hourly_year':  hourly_year,
        'hourly_month': hourly_month,
        'duration_hist': {'labels': dur_labels, 'counts': dur_counts},
        'frequency_hist': {'labels': freq_labels, 'counts': freq_counts},
        'station_totals': station_totals,
    }

    CachedStats.objects.update_or_create(key='main', defaults={'data': data})
    return f"Statistics generated: {total_events} events, {total_multibolid} multibolids"
