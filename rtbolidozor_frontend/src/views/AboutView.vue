<template>
  <div>
    <section class="hero is-medium is-dark mb-5">
      <div class="hero-body has-text-centered">
        <p class="title">About Bolidozor</p>
      </div>
    </section>
    <div class="container" style="max-width:800px;">
      <div class="box">
        <div class="dark-content">
          <p>
            <strong>Bolidozor</strong> is a network dedicated to the detection and analysis of meteors using radio signals. The network operates by detecting reflections of signals from the <a href="https://fr.wikipedia.org/wiki/Graves_(radar)" target="_blank">Graves transmitter</a>, which reflect off ionized trails left behind by meteors as they enter Earth's atmosphere.
          </p>
          <p>
            This page provides <strong>real-time data</strong> and visualizations of measurements collected by various stations across the network. Each station works autonomously, utilizing GPS for accurate time synchronization. Stations use <a href="https://www.openhardware.io/" target="_blank">open-source hardware</a> built with the <a href="https://mlab.cz" target="_blank">MLAB kit</a>.
          </p>
          <p>
            Bolidozor's mission is to monitor meteor activity and serve as a platform for long-term scientific research and public education. Through collaborations with academic institutions, we contribute to the understanding of meteors and their impact on Earth's atmosphere. Learn more at <a href="https://bolidozor.cz" target="_blank">bolidozor.cz</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dark-content { color: #94a3b8; font-size: 1.05rem; line-height: 1.8; }
.dark-content strong { color: #e2e8f0; }
.dark-content a { color: #3b82f6; }
.dark-content a:hover { color: #60a5fa; }
.dark-content p { margin-bottom: 1.2rem; }
</style>
