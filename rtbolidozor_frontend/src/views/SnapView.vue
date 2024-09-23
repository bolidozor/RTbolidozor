

<template>

    <section class="hero is-medium is-dark mb-6">
        <div class="hero-body has-text-centered">
            <p class="title mb-6">Parallel snapshot viewer</p>
        </div>
    </section>

      
      
    <div class="container.is-widescreen">

    <input  type="datetime-local"  v-model="selectedTime"  @change="onTimeChange" /><br>
    <button @click="showFurtherSnapshot" class="button btn-large" > <span class="icon is-large"><i class=" fa-lg fa-solid fa-caret-up"></i></span></button><br>
    <div class="stations-container" >
    <div class="station-column" v-for="(station, index) in stations" :key="index">



      <h3 class="bold">{{ station.station_info.name }}</h3>
      <h3>({{station.station_info.location}})</h3>

      <div>{{ station.snapshots[0].timestamp}} + 1min</div>
      <img v-for="snapshot in station.snapshots" class="snapshot-image" :src="`https://rtbolidozor.astro.cz/f.png?${snapshot.snap_file.link}`" ></img>
      
     

    </div>
    <div v-if="stations.length===0" style="width: 100%;">
      <div class="notification is-warning">
        No data for required time <time>{{ selectedTime }}</time>
      </div>
    </div>
  </div>
  <button @click="showPreviousSnapshot" class="button btn-large" ><span class="icon is-large"><i class=" fa-lg fa-solid fa-caret-down"></i></span></button>
</div>
  
  
    <div class="container">
      <div class="content">
        <h3 class="title is-3">Continuous Signal Previews from Bolidozor Stations</h3>
  
  <p>This page displays continuous snapshots of the signal from Bolidozor network stations. Each column represents one station, showing 3-minute snapshots. The oldest data is at the bottom, and the newest is at the top. </p>
  
  <p>Since snapshots are not taken at the exact same time, there might be a slight time shift between them, up to one minute. To help with this, we display three snapshots stacked vertically, each covering a 3-minute period. </p>
  
  <p>You can browse through time using the buttons above and below the images.Snapshot view </p>
  
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
        stations: [],
        snapshotsTime: null,
        }
    },
    components: {
    },
    mounted() {
      this.setInitialTimeFromURL();  // Načteme čas z URL při vstupu na stránku
      this.fetchSnapshotsByTime(this.snapshotsTime);  // Načteme data podle času
          
    },
    methods: {


    // Načte čas z URL parametrů při načtení stránky
    setInitialTimeFromURL() {
      const urlParams = new URLSearchParams(window.location.search);
      const timeFromURL = urlParams.get('time');
      if (timeFromURL) {
        this.selectedTime = timeFromURL;
        this.snapshotsTime = new Date(timeFromURL + 'Z');

      } else {
        this.snapshotsTime = new Date(new Date().getTime() - 60 * 60 * 1000);
        this.selectedTime = this.snapshotsTime.toISOString().slice(0, 16);

        this.fetchSnapshotsByTime(this.snapshotsTime);
      }
    },


    onTimeChange() {
      const params = new URLSearchParams(window.location.search);
      params.set('time', this.snapshotsTime.toISOString().slice(0, 16));
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, '', newUrl);

      this.fetchSnapshotsByTime(this.snapshotsTime);
    },


    // Funkce, která bude načítat data na základě vybraného času
    fetchSnapshotsByTime(time) {
      // URL přizpůsobené podle času
      const apiUrl = `https://rtbolidozor.astro.cz/api/v1/snapshots/${time.toISOString().slice(0, 19).replace(/[:\-]/g, '') }/`;

      // Fetch pro načtení dat podle času
      fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
          console.log('Snapshots fetched for time:', time, data);
          this.stations = data;
            
        })
        .catch(error => console.error('Error fetching snapshots:', error));
    },
        
    
    fetchSnapshots() {
        fetch('https://rtbolidozor.astro.cz/api/v1/snapshots/20240913T114840666/')
            .then(response => response.json())
            .then(data => {
                this.stations = data;  // Uložíme seznam stanic do `stations`
                
            })
            .catch(error => console.error('Error fetching snapshots:', error));  
    },

    showFurtherSnapshot() {
      this.snapshotsTime.setMinutes(this.snapshotsTime.getMinutes() + 1);

      const params = new URLSearchParams(window.location.search);
      params.set('time', this.snapshotsTime.toISOString().slice(0, 19));
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, '', newUrl);

      // Zde můžete zavolat funkci na načtení dat podle nového času
      console.log('Nový čas vybrán:', this.snapshotsTime);
      this.fetchSnapshotsByTime(this.snapshotsTime);
    },


    showPreviousSnapshot() {
      this.snapshotsTime.setMinutes(this.snapshotsTime.getMinutes() - 1);

      const params = new URLSearchParams(window.location.search);
      params.set('time', this.snapshotsTime.toISOString().slice(0, 19));
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, '', newUrl);

      // Zde můžete zavolat funkci na načtení dat podle nového času
      this.fetchSnapshotsByTime(this.snapshotsTime);

    },
  }
}
  
  </script>
  


  <style scoped>
  .stations-container {
    display: flex;
    flex-direction: row;
    overflow: auto;
    /* justify-content: space-around; */
    /* flex-wrap: wrap; */ /* Zajistí, že pokud je více stanic, budou se řadit na další řádek */
  }
  
  .station-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 10px;
    border: 1px solid #ccc;
    margin: 10px;
    width: 300px;
  }
  
  .snapshot {
    margin: 0 0;
  }
  
  .snapshot-image {
    width: 250pt;
    height: auto;  /* Zachovává poměr stran obrázků */
    margin: 0pt;
  }
  </style>