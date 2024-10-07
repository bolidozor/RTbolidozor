<template>


<div class="">

    <!-- Pagination Component -->
    <nav class="pagination" role="navigation" aria-label="pagination">
      <span> actual page: {{ current }} </span>
      <button class="pagination-previous" :disabled="!previous" @click="goToPage(previous)">Previous</button> 
      <button class="pagination-next" :disabled="!next" @click="goToPage(next)">Next</button>
    </nav>

<div v-for="group in groups" :key="group.id" class="box">
    {{ group.id }} {{ group.timestamp }}

    <table class="table is-bordered" >
        <tr style="font-weight: bold;">
            <td>Station</td>
            <td>Start time</td>
            <td>Duration</td>
            <td>Files</td>
        </tr>
        <tr v-for="event in group.events">
            <td>{{ event.station.name }}</td>
            <td>{{ event.obs_start_time }}</td>
            <td>{{ event.duration }}</td>
            <td> <a :href="event.met_file.link">met</a>, <a :href="event.raw_file.link">raw</a></td>
        </tr>
    </table>
    <div class="container" style="width: 100%;">
        <div class="stations-container">
            <div v-for="event in group.events" :key="event.id" class="station-column">
                <h3 class="bold">{{ event.station.name }}</h3>
                <div>{{ event.obs_start_time }}</div>
                <img class="snapshot-image" :src="`https://rtbolidozor.astro.cz/f.png?${event.met_file.link}`" />
                <div>{{ event.duration ? event.duration + 's' : 'N/A' }}</div>
            </div>
        </div>
    </div>

    <div>

        <a :href="`/SnapView?time=${group.timestamp.slice(0, -1)}`" target="_blank" title="Show event in SnapViewer">
            <i class="fas fa-search"></i>
        </a>
    </div>

</div>

    <!-- Pagination Component -->
    <nav class="pagination" role="navigation" aria-label="pagination">
      <span> actual page: {{ current }} </span>
      <button class="pagination-previous" :disabled="!previous" @click="goToPage(previous)">Previous</button> 
      <button class="pagination-next" :disabled="!next" @click="goToPage(next)">Next</button>
    </nav>

</div>

</template>

<script>
import axios from 'axios'
export default {
  name: 'About',
    data() {
        return {
            groups: [],
            next: null,
            previous: null,
            current: 1,
        }
    },
    mounted() {
        this.getGroups('/api/v1/multiStationEvent/')
    },
    methods: {
        async getGroups(url){
            axios
                .get(url)
                .then(response => {
                    console.log(response.data)
                    this.groups = response.data.results
                    this.next = response.data.next.replace('http://', 'https://')
                    this.previous = response.data.previous.replace('http://', 'https://')

                })
                .catch(error => {
                    console.log(error)
                })
        }, 
        goToPage(url) {
        if (url) {
            const urlParams = new URLSearchParams(url.split('?')[1]);
            this.current = urlParams.get('page') || 1;
            this.getGroups(url);
        }
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
  color: gray;
  margin: 10px;
  width: 300px;
}

.snapshot {
  margin: 0 0;
}

.snapshot-image {
  /* width: 250pt; */
  height: auto;  /* Zachovává poměr stran obrázků */
  margin: 0pt;
}
</style>