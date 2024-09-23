
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

                            #print("Met_snap file: ", file)
                            datetime_obj = datetime.strptime(name[0:17], "%Y%m%d%H%M%S%f").replace(tzinfo=timezone.utc)
                            #datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)

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
                            #if not oevent:
                            except Exception as e:
                                oevent = Event(met_file=ofile, raw_file=rfile, station_id=ostat.identifier, obs_start_time=datetime_obj)
                                ofile.event_met = oevent
                            
                            fits_header = fits.getheader(file, 1)
                            d = fits_header['DATE']
                            oevent.obs_start_time = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                            oevent.save()

                            ofile.indexed = True
                            ofile.save()

                        if 'meta.csv' in file and check_meta:
                            print("Meta file: ", file)
                            
                            sfile, needs_to_parse = File.objects.update_or_create(name=name, defaults={'file_path': file, 'hash': md5Checksum(file), 'indexed': True, 'server': 'space'})

                            if not needs_to_parse:
                                if md5Checksum(file) != sfile.hash:
                                    print("Hash changed")
                                    sfile.hash = md5Checksum(file)
                                    sfile.save()
                                    needs_to_parse = True
                            
                            if needs_to_parse:
                                print("Parsing meta file: ", file)
                                df = pd.read_csv(file, sep=';', header=0, index_col=0)
                                for index, row in df.iterrows():
                                    #print("Row: ", row)
                                    #print("Index: ", index)

                                    obj = File.objects.filter(name=index).first()

                                    if obj:
                                        if 'snap' in index:
                                            try:
                                                #osnap = obj.snapshots
                                                #osnap.save()
                                                pass
                                            except Exception as e:
                                                print("Error metadata-snap: ", e)
                                        elif 'met' in index:
                                            try:
                                                try:
                                                    oevent = obj.event_met
                                                except Exception as e:
                                                    oevent = Event(met_file=obj, station_id=index.split['_'][1], obs_start_time=row[' start time'])
                                                    obj.event_met = oevent
                                                    obj.save()
                                                oevent.peak_frequency = row[' peak f.']
                                                oevent.magnitude = row[' mag.']
                                                oevent.duration = row[' duration']
                                                #oevent.noise = row[' noise']
                                                oevent.save()
                                                pass
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
    def __init__(self, min_duration_bolid=3, min_duration=1, max_offset=5):
        self.min_duration_bolid = min_duration_bolid
        self.min_duration = min_duration
        self.max_offset = timedelta(seconds=max_offset)
        self.cluster_time_tolerance = timedelta(seconds=8)

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
            obs_start_time__range=(datetime.now() - timedelta(days=30), datetime.now())  # Upravte rozsah podle potřeby
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