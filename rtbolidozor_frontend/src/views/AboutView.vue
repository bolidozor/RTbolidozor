<template>
<section class="section" id="about">
  <div class="container">
    <h1 class="title">About Bolidozor</h1>
    <div class="content">
      <p>
        <strong>Bolidozor</strong> is a network dedicated to the detection and analysis of meteors using radio signals. The network operates by detecting reflections of signals from the <a href="https://fr.wikipedia.org/wiki/Graves_(radar)" target="_blank">Graves transmitter</a>, which reflect off ionized trails left behind by meteors as they enter Earth's atmosphere. This allows us to collect valuable data about meteor activity.
      </p>
      <p>
        The page you are viewing provides <strong>real-time data</strong> and visualizations of the measurements collected by various stations across our network. Each station works autonomously, utilizing GPS for accurate time synchronization and calibrated oscillators to ensure precise measurements. Our stations use <a href="https://www.openhardware.io/" target="_blank">open-source hardware</a> built with the <a href="https://mlab.cz" target="_blank">MLAB kit</a> and continuously provide streams of data for analysis.
      </p>
      <p>
        Bolidozor's mission is not only to monitor meteor activity but also to serve as a platform for long-term scientific research and public education. Through collaborations with academic institutions, we contribute to the understanding of meteors and their impact on Earth's atmosphere. Learn more about our work at <a href="https://bolidozor.cz" target="_blank">Bolidozor.cz</a>.
      </p>
    </div>
  </div>
</section>
</template>

<style scoped>

#about {
  background-color: #f5f5f5;
  padding: 2rem 1.5rem;
  border-radius: 8px;
}

#about .title {
  text-align: center;
  color: #3273dc;
}

#about .content {
  font-size: 1.125rem;
  line-height: 1.8;
}

#about p {
  margin-bottom: 1.5rem;
}

</style>