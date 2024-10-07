<template>


  <div id="app">
    <nav class="navbar is-dark">
      <div class="navbar-brand">
        <router-link to="/" class="navbar-item">RTBolidozor</router-link>
        
        <a :class="{'is-active': isActive}" class="navbar-burger" @click="toggleNavbar" aria-label="menu" aria-expanded="false" data-trigger="navbar-menu">
          <span aria-hidden="true"> Home </span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="navbar-menu" :class="{'is-active': isActive}" class="navbar-menu">
        <div class="navbar-end">
          <router-link to="/" class="navbar-item">Home</router-link>
          <router-link to="/map" class="navbar-item">Map</router-link>
          <router-link to="/multibolid" class="navbar-item">Multibolid</router-link>
          <router-link to="/SnapView" class="navbar-item">SnapV</router-link>
          <router-link to="/stations" class="navbar-item">Stations</router-link>
          <router-link to="/about" class="navbar-item">About</router-link>
          <router-link to="/contact" class="navbar-item">Contact</router-link>

          <div class="navbar-item">
            <div class="buttons">
              <a href="https://bolidozor.imo.net/" class="button is-warning" target="_blank">
                Report a Fireball
              </a>
            </div>
          </div>
          <!-- <div class="navbar-item">
            <div class="buttons">
              <router-link to="/login" class="button is-primary">
                <strong>Login</strong>
              </router-link>
            </div>
          </div> -->

        </div>
      </div>

    </nav>

    <section :class="sectionClass">
      <router-view/>
    </section>

    <footer class="footer" v-if="showFooter">
      <div class="content has-text-centered">
        <p>
          <strong>RTBolidozor</strong>
        </p>
      </div>
    </footer>
  </div>
  
</template>

<script>
export default {
  data() {
    return {
      isActive: false
    }
  },
  computed: {
    showFooter() {
      return this.$route.path !== '/map'
    },
    sectionClass() {
      switch (this.$route.path) {
        case '/map':
          return 'full-screen-section';
        default:
          return 'section';
      }
    }
  },
  methods: {
    toggleNavbar() {
      this.isActive = !this.isActive
    }
  }
}
</script>

<style lang="scss">
@import '../node_modules/bulma';


html, body, #app, #map-container {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}


.section {

}

.full-screen-section {
  padding: 0;
}

</style>
