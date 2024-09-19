from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Observatory, Station, Snapshot
from .serializers import ObservatorySerializer, StationSerializer, SnapshotSerializer
from django.db.models import F, ExpressionWrapper, DurationField

from django.utils import timezone
from datetime import timedelta


from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class ObservatoryList(APIView):
    def get(self, request):
        observatories = Observatory.objects.all()
        serializer = ObservatorySerializer(observatories, many=True)
        return Response(serializer.data)

class ObservatoryDetail(APIView):
    def get(self, request, identifier):
        observatory = Observatory.objects.get(identifier=identifier)
        serializer = ObservatorySerializer(observatory)
        return Response(serializer.data)

class StationList(APIView):
    def get(self, request):
        status = request.query_params.get('status', None)

        if status:
            stations = Station.objects.filter(status=status)
        else:
            stations = Station.objects.all()

        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)
    
class StationDetail(APIView):
    def get(self, request, identifier):
        station = Station.objects.get(identifier=identifier)
        serializer = StationSerializer(station)
        return Response(serializer.data)


class SnapshotListAtTime(APIView):
    def get(self, request, timestamp_str):
        print("SnapshotListAtTime")
        print("Request: ", timestamp_str)
        # Získání časového okamžiku z query parametru
        #timestamp_str = request.query_params.get('timestamp', None)
        if not timestamp_str:
            return Response({"error": "Timestamp is required"}, status=400)

        try:
            timestamp = timezone.datetime.fromisoformat(timestamp_str)

        except ValueError:
            return Response({"error": "Invalid timestamp format"}, status=400)
        
        print("...............")
        print("Timestamp: ", timestamp)

        # Najít snapshoty, které obsahují tento časový okamžik
        snapshots = Snapshot.objects.filter(
            #station_id=station_id,
            timestamp__gte=timestamp - timedelta(seconds=60),
            timestamp__lte=timestamp
            #timestamp__lte=ExpressionWrapper(
            #    F('timestamp') + 60 * timedelta(seconds=1), 
            #    output_field=DurationField()
            #)
            
        ).order_by('timestamp').order_by('station')
        station_snapshots = {}
        for snap in snapshots:
            station_id = snap.station.identifier
            if station_id not in station_snapshots:
                station_snapshots[station_id] = {
                    'station_info': StationSerializer(snap.station).data,
                    'snapshots': []
                }
            station_snapshots[station_id]['snapshots'].append(SnapshotSerializer(snap).data)

        obj = list(station_snapshots.values())
        
        return Response(obj)
        # Získání seznamu stanic
        stations = Station.objects.all()
        station_serializer = StationSerializer(stations, many=True)

        # Vytvoření odpovědi s metadaty a daty
        response_data = {
            "metadata": {
            "stations": station_serializer.data
            },
            "data": SnapshotSerializer(snapshots, many=True).data
        }

        return Response(response_data)



def realtime_event(request):
    msg = request.GET.get('msg', '')
    station_identifier = request.GET.get('station', '')
    observatory = request.GET.get('observatory', '')

    print("Event", request)

    #station = Station.objects.get(identifier=station_identifier)


    message = {
        'type': 'event',
        'station': station_identifier,
        'observatory': observatory,
    }

    channel_layer = get_channel_layer()
    print("Sending message: ", message)
    print("Channel layer: ", channel_layer)

    # Vysílání zprávy do skupiny "broadcast_group"
    async_to_sync(channel_layer.group_send)('rtmap_group',
        {
            "type": "bz_event",
            "message": message,
        }
    )
    return JsonResponse({'status': 'OK'})
