
from django_q.tasks import async_task
import time 
from datetime import datetime, timedelta, timezone
import glob2
import re
import os
import hashlib

from .models import Snapshot, File, Event, Station
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

        
def file_index(param1=None, param2=None):
    print("Task1 started: ", param1, param2)
    start = datetime.now()
    print("...........................")
    print("........................")

    time_end = datetime.now(timezone.utc)
    time_start = time_end - timedelta(days=1)


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
                        if 'snap' in file and '.fits' in name:
                            if True:

                                #print("Name: ", name)
                                datetime_obj = datetime.strptime(name[0:17], "%Y%m%d%H%M%S%f")
                                datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)

                                ofile = File.objects.filter(name=name).first()
                                if not ofile:
                                    #print("New file: ", file)
                                    ofile = File(file_path=file, name=name, hash=md5Checksum(file))
                                    ofile.save()
                                
                                osnap = ofile.snapshots
                                if not osnap:
                                    osnap = Snapshot(snap_file=ofile, station_id=ostat.identifier, timestamp=datetime_obj, duration=60000)
                                
                                fits_header = fits.getheader(file, 1)
                                d = fits_header['DATE']
                                osnap.timestamp = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")                                
                                
                                osnap.save()

                                ofile.indexed = True
                                ofile.save()

                        if '_met.fits' in file:

                            #print("Met_snap file: ", file)
                            datetime_obj = datetime.strptime(name[0:17], "%Y%m%d%H%M%S%f")
                            datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)

                            ofile = File.objects.filter(name=name).first()
                            if not ofile:
                                print("New file: ", file)
                                ofile = File(file_path=file, name=name, hash=md5Checksum(file))
                                rfile = File(file_path=file.replace('met.', 'raws.'), name=name.replace('met.', 'raws.'), online=False)
                                ofile.save()
                                rfile.save()
                            
                            oevent = ofile.event_met
                            if not oevent:
                                oevent = Event(met_file=ofile, raw_file=rfile, station_id=ostat.identifier, obs_start_time=datetime_obj)
                            
                            fits_header = fits.getheader(file, 1)
                            d = fits_header['DATE']
                            oevent.obs_start_time = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S")
                            oevent.save()

                            ofile.indexed = True
                            ofile.save()

                        if 'meta.csv' in file:
                            print("Meta file: ", file)
                            pass


                    except Exception as e:
                        print("Error: ", e)
                        pass
        

    print("Task1 done: ", datetime.now() - start)
    return "Task1 done, duration {}".format(datetime.now() - start)


# def spustit_uloha():
#     async_task('rtbolidozor_backend.tasks.file_index', 'param1', 'param2')