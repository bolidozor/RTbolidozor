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
        v-for="observatory in sortedObservatories"
        v-bind:key="observatory.name"
      >

              <div class="card-header">
                <a :href="'#' + observatory.name" class="card-header-icon">
                  <span class="icon">
                    <i class="fas fa-link"></i>
                  </span>
                </a>
              <p class="card-header-title">{{observatory.identifier}}, {{observatory.name}} <br> {{ observatory.location }}</p>
              </div>

              <div class="card-content">
                <div class="content">
                  
              <div 
                class="station m-4"
                v-for="station in [...observatory.stations].reverse()"
                v-bind:key="station.identificator"
              >
                  <div class="tag is-llight-primary is-medium"><b>{{station.identifier}}</b>
                    <span 
                    class="tag ml-2" 
                    :class="{
                      'is-success': ['active'].includes(station.status),
                      'is-warning': ['maintenance', 'updating'].includes(station.status),
                      'is-danger': ['error'].includes(station.status),
                      'is-dark': ['pending', 'retired'].includes(station.status)
                    }"
                    >
                    {{ station.status }}
                    </span>
                  </div>

                  <div v-if="station.status === 'active'" class="rmob-card">
                    <img
                      :src="`https://space.astro.cz/bolidozor/support/rmob/${station.identifier}_` + new Date().toLocaleDateString('en-GB').slice(3).replace(/\//g, '') + `.svg`"
                      alt="RMOB preview"
                      class="rmob-img"
                    />
                  </div>
              </div>
              </div>
              </div>
      </div>
      {{ observatories.length }}
    <div v-if="observatories.length === 0" class="notification is-warning">
      No data for required time <time>{{ selectedTime }}</time>
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
  computed: {
    sortedObservatories() {
      const hasOnline = obs => obs.stations.some(s => s.status === 'active')
      return [...this.observatories].sort((a, b) => {
        const aOnline = hasOnline(a) ? 1 : 0
        const bOnline = hasOnline(b) ? 1 : 0
        if (bOnline !== aOnline) return bOnline - aOnline
        return b.identifier.localeCompare(a.identifier)
      })
    }
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

<style scoped>
.rmob-card {
  display: inline-block;
  background: #1e2a3a;
  border: 1px solid #2d4060;
  border-radius: 8px;
  padding: 0.5rem;
  margin-top: 0.5rem;
}
.rmob-img {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}
</style>
