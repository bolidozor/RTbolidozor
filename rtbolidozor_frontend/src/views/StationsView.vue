<template>
  <div class="stations">
    <section class="hero is-medium is-dark mb-6">
        <div class="hero-body has-text-centered">
            <p class="title mb-6">
                Bolidozor stations
            </p>
        </div>
    </section>


    <div class="StationsList">

      <div
        class = "card mgb-small"
        v-for="observatory in observatories"
        v-bind:key="observatory.name"
      >

              <div class="card-header">

              <p class="card-header-title">{{observatory.identifier}}, {{observatory.name}}</p>
              </div>

              <div class="card-content">
              <div 
                class="station box"
                v-for="station in observatory.stations"
                v-bind:key="station.identificator"
              >
                  {{station.identifier}}<br>
                  {{station.name}}<br>
                  {{station.status}}
              </div>

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
      observatories: []
      }
  },
  components: {
  },
  mounted() {
    this.getStationsTree()
  },
  methods: {
    getStationsTree(){
      axios
        .get('/api/v1/observatories/')
        .then(response => {
          console.log(response.data)
          this.observatories = response.data
        })
        .catch(error => {
          console.log(error)
        })
    }
  }
}

</script>

    