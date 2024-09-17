<template>
<section class="section">
  <div class="container">
    <div class="content has-text-centered">
      <h1 class="title">RTbolidozor - Real-Time Meteor Data Visualization</h1>
      <p class="subtitle">Explore real-time data from the Bolidozor network, tracking the passage of meteors with cutting-edge radio detection technology.</p>
    </div>

    <div class="columns">
      <div class="column">
        <div class="box">
          <h2 class="title is-4">How It Works</h2>
          <p>RTbolidozor utilizes signals from the Graves transmitter, which reflect off ionized gas trails left by meteors. This allows us to monitor meteor activity with high precision.</p>
        </div>
      </div>

      <div class="column">
        <div class="box">
          <h2 class="title is-4">Real-Time Data</h2>
          <p>Stay updated with live data from our network of stations, offering immediate insights into meteor detections across various locations.</p>
        </div>
      </div>

      <div class="column">
        <div class="box">
          <h2 class="title is-4">Event Overview</h2>
          <p>Access a detailed list of recent meteor events, including time, location, and signal strength.</p>
        </div>
      </div>
    </div>

    <div class="box has-text-centered">
      <h2 class="title is-4">Activity Map</h2>
      <p>Visualize the activity of meteors in your region through interactive maps and charts.</p>
      <button class="button is-link is-medium">Explore the Map</button>
    </div>
  </div>
</section>

</template>

<script>
export default {
  name: 'HelloWorld',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
