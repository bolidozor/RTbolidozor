from rest_framework import serializers
from .models import Observatory, Station, BolidozorUser



class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = [
            'identifier',
            'name',
            'location',
            'observatory',
        ]
        
class ObservatorySerializer(serializers.ModelSerializer):
    stations = StationSerializer(many=True, read_only=True)
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