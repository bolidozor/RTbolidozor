from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Observatory, Station
from .serializers import ObservatorySerializer, StationSerializer



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
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)
        return Response(serializer.data)
    
class StationDetail(APIView):
    def get(self, request, identifier):
        station = Station.objects.get(identifier=identifier)
        serializer = StationSerializer(station)
        return Response(serializer.data)



def realtime_event(request):
    message = request.GET.get('message', 'Default message')
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
    return JsonResponse({'status': 'Message sent'})