<template>
    <div id="map-container">
      <l-map :zoom="zoom" :center="center" style="height: 100%; width: 100%;" ref="map">
        <l-tile-layer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <l-marker
          v-for="observatory in observatories"
          :key="observatory.identifier"
          :ref="`observatoryMarker-${observatory.identifier}`"
          :lat-lng="[observatory.latitude, observatory.longitude]"
          :observatory="observatory"
        >
            <l-icon>
              <i :ref="`observatoryIcon-${observatory.identifier}`" class="fa fa-circle-dot icon-inactive"></i>
            </l-icon>
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
  import { LMap, LTileLayer, LMarker, LPopup, LIcon } from '@vue-leaflet/vue-leaflet';
  import axios from 'axios'


  export default {
    name: 'MapView',
    components: {
      LMap,
      LTileLayer,
      LMarker,
      LPopup,
      LIcon
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
      this.setupWebSocket();
    },

    computed: {
      iconUrl() {
        return `https://placekitten.com/${this.iconWidth}/${this.iconHeight}`;
      },
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
      },
      setupWebSocket() {
      this.socket = new WebSocket('wss://rtbolidozor.astro.cz/ws/');

      this.socket.onopen = () => {
        console.log('WebSocket connection opened');
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Event recieved:', data);
        this.handleWebSocketMessage(data);
      };

      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    },
    handleWebSocketMessage(data) {
      // Příklad aktualizace observatories
      var event_obs = data.message.observatory;
      console.log('HandleWebsocket:', event_obs);
      console.log(this.observatories);
      
      const obs_object = this.observatories.find(obs => obs.identifier === event_obs);
      console.log("Maarker", obs_object);

      const refName = `observatoryIcon-${event_obs}`;
      console.log("REF", refName);
      if (this.$refs[refName]) {
        console.log(this.$refs[refName]);
        this.$refs[refName][0].classList.remove('icon-inactive', 'icon-active');
        this.$refs[refName][0].classList.add('icon-event');

        setTimeout(() => {
          this.$refs[refName][0].classList.remove('icon-event');
          this.$refs[refName][0].classList.add('icon-active');
        }, 3000);
      }
      

      
    },
  },
  beforeDestroy() {
    if (this.socket) {
      this.socket.close();
    }
  },
  };
  </script>
  
  <style scoped>

@keyframes blink {
  0%, 50%, 100% {
    opacity: 1;
    size: 2em;
  }
  25%, 75% {
    opacity: 0;
    size: 2.5em;
  }
}

  #map-container {
    height: 100vh;
    width: 100vw;
    margin: 0;
    padding: 0;
  }

  .section {
    padding: 0% !important;
  }

  .icon-inactive {
    width: 1em;
    height: 1em;
    background-color: grey;
    border-radius: 50%;
  }

  .icon-active {
    width: 1.5em;
    height: 1.5em;
    background-color: black;
    border-radius: 50%;
  }

  .icon-event {
    width: 2em;
    height: 2em;
    background-color: green;
    border-radius: 50%;
    animation: blink 1s infinite;
  }

  </style>
  
