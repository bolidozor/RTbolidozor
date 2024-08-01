import os
import configparser
import django
import sys

sys.path.append('../rtbolidozor_backend')
sys.path.append('../app')

# Inicializace Django prostředí
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtbolidozor_backend.settings')
django.setup()

from rtbolidozor_backend.models import Observatory, Station

def parse_rmob_conf(conf_path):
    config = configparser.ConfigParser()
    config.read(conf_path)
    
    if 'RmobConfig' in config:
        station_info = config['RmobConfig']
        return {
            'station_name': station_info.get('stationname', 'N/A'),
            'country': station_info.get('country', 'N/A'),
            'city': station_info.get('city', 'N/A'),
            'latitude': station_info.get('latitudedeg', '0.0'),
            'longitude': station_info.get('longtitudedeg', '0.0'),
            'email': station_info.get('email', 'N/A'),
            'computer': station_info.get('computer', 'N/A'),
            'antenna': station_info.get('antenna', 'N/A'),
            'preamp': station_info.get('preamp', 'N/A'),
            'receiver': station_info.get('reciver', 'N/A'),
            'frequency': station_info.get('frequency', 'N/A')
        }
    return None

def process_directory(root_dir):
    for obs_name in os.listdir(root_dir):
        obs_path = os.path.join(root_dir, obs_name)
        if os.path.isdir(obs_path):
            for station_name in os.listdir(obs_path):
                station_path = os.path.join(obs_path, station_name)
                print(station_path)
                if os.path.isdir(station_path):
                    conf_path = os.path.join(station_path, 'rmob.cfg')
                    if os.path.isfile(conf_path):
                        station_info = parse_rmob_conf(conf_path)
                        

                        observatory, created = Observatory.objects.get_or_create(
                            identifier=obs_name,
                            defaults={
                                'name': obs_name,
                                'location': '',  # Můžete upravit nebo přidat skutečné umístění, pokud je k dispozici
                                'latitude': 0.0,  # Výchozí hodnota, může být nahrazena skutečnou hodnotou
                                'longitude': 0.0  # Výchozí hodnota, může být nahrazena skutečnou hodnotou
                            }
                        )

                        if station_info:
                            Station.objects.get_or_create(
                                identifier=station_info['station_name'],
                                defaults={
                                    'name': station_info['station_name'],
                                    'location': station_info['city'],
                                    'observatory': observatory,
                                    'status': 'pending',  # Můžete nastavit výchozí stav nebo použít stav z dat
                                }
                            )

                            observatory.latitude = station_info['latitude']
                            observatory.longitude = station_info['longitude']
                            observatory.location = station_info['country'] + ", " + station_info['city']
                            observatory.save()

def main():
    root_directory = '/storage'  # Nastavte cestu k hlavnímu adresáři
    process_directory(root_directory)

if __name__ == "__main__":
    main()
