from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Observatory, Station, Snapshot, MultiStationEvent
from .serializers import ObservatorySerializer, StationSerializer, SnapshotSerializer, MultiStationEventSerializer
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
        
        snapshots = Snapshot.objects.filter(
            #station_id=station_id,
            timestamp__gte=timestamp - timedelta(seconds=60*2),
            timestamp__lte=timestamp + timedelta(seconds=60)
            #timestamp__lte=ExpressionWrapper(
            #    F('timestamp') + 60 * timedelta(seconds=1), 
            #    output_field=DurationField()
            #)
            
        ).order_by('-timestamp', 'station')
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


class CustomPagination(PageNumberPagination):
    page_size = 5  # Definice vlastního počtu položek na stránku
    page_size_query_param = 'page_size'  # Uživatel může specifikovat velikost stránky pomocí dotazu ?page_size=
    max_page_size = 100  # Maximální povolený počet položek na stránku


class MultiStationEventViewSet(APIView):
    """
    API endpoint that allows MultiStationEvents to be viewed.
    """
    queryset = MultiStationEvent.objects.all().prefetch_related('events').order_by('-timestamp')
    serializer_class = MultiStationEventSerializer
    pagination_class = CustomPagination

    def get(self, request):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        
        events = MultiStationEvent.objects.all().order_by('-timestamp')
        result_page = paginator.paginate_queryset(events, request)
        serializer = MultiStationEventSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



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
