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

from rtbolidozor_backend.models import File, Event, EventMetadata, Station
import glob2

# Cesta k adresáři s daty
BASE_DIR = '/storage'

def parse_metadata_csv(file_path):
    """Parse the metadata CSV file and return a list of dictionaries of metadata."""
    data = pd.read_csv(file_path, delimiter=';' )
    metadata_list = []
    for _, row in data.iterrows():
        #print(row)
        metadata = {
            "file_name": row["# file name"].strip(),
            "noise": row[" noise"],
            "peak_frequency": row[" peak f."],
            "magnitude": row[" mag."],
            "duration": row[" duration"]
        }
        metadata_list.append(metadata)
    return metadata_list

def process_fits_header(file_path):
    """Extract information from the FITS file header."""
    with fits.open(file_path) as hdul:
        header = hdul[0].header
        # Extrahujte potřebné informace z hlavičky
        return str(header)

def process_directory(base_directory):
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            try:
                
                file_path = os.path.join(root, file)
                if file.endswith('meta.csv'):
                    print("Processing file:", file_path)
                    # Načíst metadata
                    metadata_list = parse_metadata_csv(file_path)

                    # Určení stanice podle cesty
                    parts = root.split(os.sep)
                    station_name = parts[-5]
                    year, month, day = parts[-3], parts[-2], parts[-1]

                    # Vytvořit nebo získat záznam stanice
                    station, created = Station.objects.get_or_create(name=station_name)

                    for metadata in metadata_list:
                        try:
                            # Vytvořit záznam pro File (metadata CSV)
                            meta_file = File.objects.create(
                                name=metadata['file_name'],
                                hash='hash_placeholder',
                                file_path=file_path
                            )

                            obs_start_time = datetime.strptime(metadata['file_name'].split('_')[0], "%Y%m%d%H%M%S%f").replace(tzinfo=timezone.utc)

                            # # Vytvořit záznam pro EventMetadata
                            # event_metadata = EventMetadata.objects.create(
                            # )

                            # Vytvořit záznam pro Event
                            event = Event.objects.create(
                                met_file=meta_file,
                                obs_start_time=obs_start_time,
                                station=station,
                                # metadata=event_metadata
                                peak_frequency=metadata['peak_frequency'],
                                magnitude=metadata['magnitude'],
                                duration=metadata['duration'],
                                corrected_time_flag=False,
                                corrected_start_time=obs_start_time
                            )
                        except Exception as e:
                            print("Error in csv file processing:", e)

                elif file.endswith('met.fits'):
                    try:
                        # Určení stanice podle cesty
                        parts = root.split(os.sep)
                        station_name = parts[-6]
                        year, month, day, hour = parts[-4], parts[-3], parts[-2], parts[-1]

                        print("Processing file:", file_path)
                        print(parts, station_name, year, month, day, hour)

                        # Vytvořit nebo získat záznam stanice
                        station = Station.objects.get(name=station_name)

                        # Vytvořit záznam pro File (FITS soubory)
                        file_header = process_fits_header(file_path)
                        file_record = File.objects.create(
                                name=file,
                                hash='hash_placeholder',
                                file_path=file_path)

                        # Najít odpovídající Event podle času a stanice
                        obs_start_time = datetime.strptime(file.split('_')[0], "%Y%m%d%H%M%S%f")
                        event = Event.objects.filter(
                                station=station,
                                obs_start_time=obs_start_time
                            ).first()

                        if event:
                            if file.endswith('met.fits'):
                                event.met_file = file_record
                            elif file.endswith('raws.fits'):
                                event.raw_file = file_record
                            event.save()
                    except Exception as e:
                        print("Error in fits file processing:", e)
            except Exception as e:
                print("Error in file processing:", e)

if __name__ == "__main__":
    process_directory(BASE_DIR)
