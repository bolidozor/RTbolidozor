

import 'https://js9.si.edu/js9/js9support.min.js';
import 'https://js9.si.edu/js9/js9.min.js';
import 'https://js9.si.edu/js9/js9plugins.js';
import 'https://js9.si.edu/js9/js9.css';
import 'https://js9.si.edu/js9/js9support.css';


<template>
    <div class="stations">
      <section class="hero is-medium is-dark mb-6">
        SnapV
      </section>


      <input 
      type="datetime-local" 
      v-model="selectedTime" 
      @change="onTimeChange"
    />

      <div class="">


    <div class="JS9Menubar"></div>
    <div class="JS9"></div>
    <div class="JS9Statusbar"></div>

        </div>



      <div class="stations-container">
    <div class="station-column" v-for="(station, index) in stations" :key="index">



        <h3>{{ station.station_info.name }} ({{station.station_info.location}})</h3>
        <p>{{ station.station_info }}</p>
      
      <!-- Procházíme snapshoty pro stanici -->
      <div v-for="(snapshot, sIndex) in station.snapshots" :key="sIndex" class="snapshot">

        <!-- Vykreslíme obrázek pro každý snapshot -->
        {{ snapshot.snap_file }}
      </div>

    </div>
  </div>


    <div class="columns is-multiline"></div>
        <div class="column is-one-quarter" v-for="station in observatories.flatMap(obs => obs.stations)" :key="station.identificator">
            <div class="card">
                <div class="card-content">
                    <p class="title">{{ station.identifier }}</p>
                    <p class="subtitle">{{ station.status }}</p>
                </div>
            </div>
        </div>
    </div>


    
  
  </template>
  
  
  
  <script>
  import axios from 'axios'
  export default {
    name: "Stations",
    data() {
      return {
        observatories: [],
        stations: []
        }
    },
    components: {
    },
    mounted() {
      this.setInitialTimeFromURL();  // Načteme čas z URL při vstupu na stránku
      this.fetchSnapshots();
          
    },
    methods: {


    // Načte čas z URL parametrů při načtení stránky
    setInitialTimeFromURL() {
      const urlParams = new URLSearchParams(window.location.search);
      const timeFromURL = urlParams.get('time');
      if (timeFromURL) {
        // Pokud je čas v URL, nastavíme datetime picker
        this.selectedTime = timeFromURL;
      }
    },


    // Funkce, která se volá, když se čas změní
    onTimeChange() {
      // Změníme URL bez znovunačítání stránky
      const params = new URLSearchParams(window.location.search);
      params.set('time', this.selectedTime);
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, '', newUrl);

      // Zde můžete zavolat funkci na načtení dat podle nového času
      console.log('Nový čas vybrán:', this.selectedTime);
      this.fetchSnapshotsByTime(this.selectedTime);
    },


    // Funkce, která bude načítat data na základě vybraného času
    fetchSnapshotsByTime(time) {
      // URL přizpůsobené podle času
      const apiUrl = `https://rtbolidozor.astro.cz/api/v1/snapshots/${time}/`;

      // Fetch pro načtení dat podle času
      fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
          console.log('Snapshots fetched for time:', time, data);
          this.stations = data;
            this.$nextTick(() => {
                this.showSnapshot();
            });
        })
        .catch(error => console.error('Error fetching snapshots:', error));
    },
        
    
    fetchSnapshots() {
        fetch('https://rtbolidozor.astro.cz/api/v1/snapshots/20240913T114840666/')
            .then(response => response.json())
            .then(data => {
                this.stations = data;  // Uložíme seznam stanic do `stations`
                this.$nextTick(() => {
                    this.showSnapshot();
                });
            })
            .catch(error => console.error('Error fetching snapshots:', error));  
    },

    showSnapshot() {
        console.log('Showing snapshot:');
        this.stations.forEach(station => {
            station.snapshots.forEach(snapshot => {
                console.log(snapshot.snap_file.file_path.substring(15), station.station_info.identifier);
                const url = `https://space.astro.cz/bolidozor/${snapshot.snap_file.file_path.substring(15)}`;

                JS9.Load(url);

            });
        });
    },
  }
}
  
  </script>
  


  <style scoped>
  .stations-container {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    flex-wrap: wrap; /* Zajistí, že pokud je více stanic, budou se řadit na další řádek */
  }
  
  .station-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    border: 1px solid #ccc;
    margin: 10px;
  }
  
  .snapshot {
    margin: 5px 0;
  }
  
  .snapshot-image {
    width: 200px;
    height: auto;  /* Zachovává poměr stran obrázků */
    border: 1px solid #000;
  }
  </style>