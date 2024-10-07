<template>
<section class="section">
  <div class="container">
    <div class="box has-text-centered">
      <h1 class="title is-h1">RTbolidozor - Real-Time Meteor Data Visualization</h1>
      <p class="subtitle">Explore real-time data from the Bolidozor network, tracking the passage of meteors with cutting-edge radio detection technology.</p>
    </div>

    <div class="columns is-flex is-align-items-stretch">
      <div class="column is-flex">
      <div class="box is-flex is-flex-direction-column is-fullheight">
        <h2 class="title is-4">How It Works</h2>
        <p>RTbolidozor utilizes signals from the Graves transmitter, which reflect off ionized gas trails left by meteors. This allows us to monitor meteor activity with high precision.</p>
      </div>
      </div>

      <div class="column is-flex">
      <div class="box is-flex is-flex-direction-column is-fullheight">
        <h2 class="title is-4">Real-Time Data</h2>
        <p>Stay updated with live data from our network of stations, offering immediate insights into meteor detections across various locations.</p>
      </div>
      </div>

      <div class="column is-flex">
      <div class="box is-flex is-flex-direction-column is-fullheight">
        <h2 class="title is-4">Event Overview</h2>
        <p>Access a detailed list of recent meteor events, including time, location, and signal strength.</p>
      </div>
      </div>
    </div>

    <div class="box has-text-centered">
      <h2 class="title is-4">Activity Map</h2>
      <p>Visualize the activity of meteors in your region through interactive map.</p>

      <router-link to="/map">
        <button class="button is-link">Explore the Map</button>
      </router-link>
    </div>
    
      <div class="box has-text-centered">
        <h3 class="title is-4">Have You Seen a Bolide?</h3>
        <p>If you've witnessed a bolide, we encourage you to report it to the International Meteor Organization's observer database at <a href="https://bolidozor.imo.net" target="_blank">bolidozor.imo.net</a>. Your observation can contribute to discovering many fascinating details about the event and help advance scientific research. Every report counts, and your participation could provide valuable data for scientists studying meteors and bolides.</p> 

          <a href="https://bolidozor.imo.net/" class="button is-warning" target="_blank">
            Report a Fireball
          </a>

    </div>
  </div>
</section>

</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'

export default {
  name: 'Home',
  components: {
  }
}
</script>
