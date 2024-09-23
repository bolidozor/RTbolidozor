<template>


<div class="">
<div v-for="group in groups" :key="group.id" class="box">
    {{ group.id }}
    <table class="table is-bordered">
    <tr v-for="event in group.events">
        <td>{{ event.station.name }}</td>
        <td>{{ event.obs_start_time }}</td>
        <td>{{ event.duration }}</td>
        <td> <a :href="event.met_file.link">met</a>, <a :href="event.raw_file.link">raw</a></td>

    </tr>
</table>
    <div class="container.is-widescreen">
    <div class="station-container">
        <div v-for="event in group.events" class="station-column">
            <img class="snapshot-image" :src="`https://rtbolidozor.astro.cz/f.png?${event.met_file.link}`" ></img>
        </div>
    </div>
    </div>

</div>

    <!-- Pagination Component -->
    <nav class="pagination is-centered" role="navigation" aria-label="pagination">
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
            previous: null
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
                    this.next = response.data.next
                    this.previous = response.data.previous
                })
                .catch(error => {
                    console.log(error)
                })
        }, 
        goToPage(url) {
        if (url) {
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