<template>
    <div id="map-container">
      <l-map :zoom="zoom" :center="center" style="height: 100%; width: 100%;">
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <l-marker
          v-for="observatory in observatories"
          :key="observatory.identifier"
          :lat-lng="[observatory.latitude, observatory.longitude]"
        >
            <l-popup> <div class="leaflet-popup-content">
                <h3 class="text-strong">{{ observatory.name }} ({{observatory.identifier}})</h3>
                <p><strong>Location: </strong> {{ observatory.location }}</p>
                <p><strong>Stations: </strong></p>
                    <ul v-for = "station in observatory.stations">
                        <li>{{ station.identifier }} - {{ station.name }} - {{ station.status }}</li>
                    </ul>
            </div> </l-popup>
        </l-marker>
      </l-map>
    </div>
  </template>
  
  <script>
  import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';
  import axios from 'axios'
  
  export default {
    name: 'MapView',
    components: {
      LMap,
      LTileLayer,
      LMarker,
      LPopup
    },
    data() {
      return {
        zoom: 7,
        center: [49.8, 15.5],
        observatories: []
      };
    },
    mounted() {
      this.fetchObservatories();
    },
    methods: {
      fetchObservatories() {
        axios.get('/api/v1/observatories/')
        .then(response => {
          this.observatories = response.data;
        })
        .catch(error => {
          console.error('There was an error fetching the observatories:', error);
        });
      }
    }
  };
  </script>
  
  <style scoped>
  #map-container {
    height: 100vh;
    width: 100vw;
    margin: 0;
    padding: 0;
  }

  .section {
    padding: 0% !important;
  }
  </style>
  
