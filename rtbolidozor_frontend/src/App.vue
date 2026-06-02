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
          <router-link to="/events" class="navbar-item">Events</router-link>
          <router-link to="/stats" class="navbar-item">Statistics</router-link>
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
      if (this.$route.path === '/map') return 'full-screen-section';
      if (['/', '/multibolid', '/stats'].includes(this.$route.path)) return 'no-padding-section';
      return 'dark-section';
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

/* ── Base ── */
html, body {
  background: #0b0e17;
  color: #e0e6f0;
}

html, body, #app, #map-container {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #0b0e17;
}

/* ── Section wrappers ── */
.dark-section {
  background: #0b0e17;
  flex: 1;
  padding: 1.5rem;
}

.full-screen-section {
  padding: 0;
}

.no-padding-section {
  padding: 0;
  background: #0b0e17;
}

/* ── Footer ── */
.footer {
  background: #080b12 !important;
  border-top: 1px solid #1e2d45;
  color: #475569 !important;
  padding: 1.5rem;
}
.footer strong { color: #64748b !important; }

/* ── Bulma overrides for dark theme ── */
.box {
  background: #111827;
  border: 1px solid #1e2d45;
  color: #e0e6f0;
  box-shadow: none;
}

.card {
  background: #111827;
  border: 1px solid #1e2d45;
  box-shadow: none;
  color: #e0e6f0;
}
.card-header { background: #151d2e; border-bottom: 1px solid #1e2d45; box-shadow: none; }
.card-header-title { color: #e2e8f0; }
.card-content { background: #111827; }

.title { color: #e2e8f0 !important; }
.subtitle { color: #94a3b8 !important; }

.table { background: transparent; color: #94a3b8; }
.table th { color: #64748b; border-color: #1e2d45 !important; }
.table td { border-color: #1e2d45 !important; }
.table thead td, .table thead th { color: #64748b; border-color: #1e2d45 !important; }

.notification.is-warning { background: #2d1f00; color: #fbbf24; border: 1px solid #92400e; }
.notification.is-danger  { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.notification.is-info    { background: #0a1f2d; color: #38bdf8; border: 1px solid #0c4a6e; }

.tag.is-light { background: #1e2d45; color: #94a3b8; }

.input, .select select, .textarea {
  background: #0f1623;
  border-color: #2d4060;
  color: #e0e6f0;
}
.input:focus, .select select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59,130,246,.25);
}
.label { color: #94a3b8; }

</style>
