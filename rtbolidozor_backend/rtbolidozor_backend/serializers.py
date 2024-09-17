from rest_framework import serializers
from .models import Observatory, Station, BolidozorUser



class StationSerializer(serializers.ModelSerializer):
    # Meta class to specify the model and fields to be used in the serializer
    class Meta:
        model = Station
        fields = [
            'identifier',
            'name',
            'location',
            'observatory',
            'status',
        ]
        
class ObservatorySerializer(serializers.ModelSerializer):
    stations = serializers.SerializerMethodField()
    #stations = StationSerializer(many=True, read_only=True)
    class Meta:
        model = Observatory
        fields = [
            'identifier',
            'name',
            'location',
            'latitude',
            'longitude',
            'stations'
        ]
    
    def get_stations(self, obj):
        stations = obj.stations.order_by('name', 'status')
        return StationSerializer(stations, many=True).data