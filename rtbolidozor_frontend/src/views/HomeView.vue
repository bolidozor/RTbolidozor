<template>
  <div class="home-view">

    <section class="hero-banner">
      <div class="hero-content">
        <div class="hero-badge"><span class="live-dot"></span>LIVE NETWORK</div>
        <h1 class="hero-title">RTbolidozor</h1>
        <p class="hero-subtitle">Real-time meteor detection across Central Europe<br>via reflected radio signals from the GRAVES transmitter</p>
        <div class="hero-actions">
          <router-link to="/map" class="btn-primary">Open Live Map</router-link>
          <router-link to="/events" class="btn-secondary">Browse Events</router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="radar-ring ring-1"></div>
        <div class="radar-ring ring-2"></div>
        <div class="radar-ring ring-3"></div>
        <div class="radar-dot"></div>
        <div class="meteor-streak s1"></div>
        <div class="meteor-streak s2"></div>
        <div class="meteor-streak s3"></div>
      </div>
    </section>

    <section class="features-section">
      <div class="container">
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">📡</div>
            <h3>Radio Detection</h3>
            <p>Passive stations receive forward-scattered signals from the 143.05 MHz GRAVES space surveillance radar in Dijon, France, reflected off meteor ionization trails.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Real-Time Data</h3>
            <p>Events are processed and published within seconds of detection. The live map and event browser update continuously as meteors are recorded across the network.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <h3>Multi-Station Correlation</h3>
            <p>When multiple stations detect the same meteor simultaneously, the system automatically groups them into a confirmed multi-station event for cross-correlation.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔭</div>
            <h3>FITS Data Access</h3>
            <p>Every detection is stored as a FITS file. Use the built-in htfits viewer or switch to the full JS9 FITS viewer for detailed spectral analysis.</p>
          </div>
        </div>
      </div>
    </section>

    <section class="nav-cards-section">
      <div class="container">
        <h2 class="section-title">Explore the Network</h2>
        <div class="nav-grid">
          <router-link to="/map" class="nav-card">
            <span class="nav-card-icon">🗺️</span>
            <span class="nav-card-label">Live Map</span>
            <span class="nav-card-desc">Station status &amp; real-time detections</span>
          </router-link>
          <router-link to="/events" class="nav-card">
            <span class="nav-card-icon">📋</span>
            <span class="nav-card-label">Event Browser</span>
            <span class="nav-card-desc">Browse, filter and view FITS data</span>
          </router-link>
          <router-link to="/multibolid" class="nav-card">
            <span class="nav-card-icon">☄️</span>
            <span class="nav-card-label">Multibolid</span>
            <span class="nav-card-desc">Multi-station correlated events</span>
          </router-link>
          <router-link to="/stations" class="nav-card">
            <span class="nav-card-icon">📻</span>
            <span class="nav-card-label">Stations</span>
            <span class="nav-card-desc">All observatories and receivers</span>
          </router-link>
          <router-link to="/SnapView" class="nav-card">
            <span class="nav-card-icon">🖼️</span>
            <span class="nav-card-label">SnapView</span>
            <span class="nav-card-desc">Snapshot browser by time</span>
          </router-link>
          <a href="https://bolidozor.imo.net/" target="_blank" class="nav-card nav-card--highlight">
            <span class="nav-card-icon">🔥</span>
            <span class="nav-card-label">Report a Fireball</span>
            <span class="nav-card-desc">Submit your visual observation to IMO</span>
          </a>
        </div>
      </div>
    </section>

    <section class="about-band">
      <div class="container">
        <p>
          Part of the international <strong>Bolidozor</strong> network — a collaborative project
          for automated radio meteor detection and research.
          <a href="https://bolidozor.imo.net" target="_blank">bolidozor.imo.net</a>
        </p>
      </div>
    </section>

  </div>
</template>

<script>
export default {
  name: 'HomeView',
}
</script>

<style scoped>
.home-view {
  background: #0b0e17;
  min-height: 100vh;
  color: #e0e6f0;
}

/* ── Hero ── */
.hero-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5rem 4rem 4rem;
  background: linear-gradient(135deg, #0b0e17 0%, #111827 60%, #0d1a2e 100%);
  position: relative;
  overflow: hidden;
  min-height: 420px;
}

.hero-content {
  max-width: 540px;
  z-index: 2;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45em;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  color: #22d3ee;
  border: 1px solid #22d3ee55;
  border-radius: 20px;
  padding: 0.2em 0.9em;
  margin-bottom: 1.2rem;
}

.live-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 6px #22d3ee;
  animation: live-pulse 2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 6px #22d3ee; }
  50%       { opacity: 0.25; box-shadow: none; }
}

.hero-title {
  font-size: 3.4rem;
  font-weight: 800;
  line-height: 1.1;
  color: #fff;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: #94a3b8;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-block;
  padding: 0.7em 1.8em;
  background: #3b82f6;
  color: #fff;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s;
}
.btn-primary:hover { background: #2563eb; color: #fff; }

.btn-secondary {
  display: inline-block;
  padding: 0.7em 1.8em;
  border: 1px solid #334155;
  color: #cbd5e1;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}
.btn-secondary:hover { border-color: #64748b; color: #fff; }

/* Radar visual */
.hero-visual {
  position: relative;
  width: 280px;
  height: 280px;
  flex-shrink: 0;
  z-index: 1;
}

.radar-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid #22d3ee22;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
}
.ring-1 { width: 100px; height: 100px; border-color: #22d3ee44; }
.ring-2 { width: 180px; height: 180px; }
.ring-3 { width: 260px; height: 260px; border-color: #22d3ee11; }

.radar-dot {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 10px; height: 10px;
  border-radius: 50%;
  background: #22d3ee;
  box-shadow: 0 0 16px 4px #22d3ee88;
}

.meteor-streak {
  position: absolute;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, transparent, #f59e0b, transparent);
  opacity: 0.7;
}
.s1 { width: 80px; top: 30%; left: 20%; transform: rotate(-30deg); }
.s2 { width: 50px; top: 60%; left: 55%; transform: rotate(-20deg); opacity: 0.4; }
.s3 { width: 65px; top: 45%; left: 10%; transform: rotate(-35deg); opacity: 0.5; }

@media (max-width: 768px) {
  .hero-banner { flex-direction: column; padding: 3rem 1.5rem 2rem; }
  .hero-visual { display: none; }
  .hero-title { font-size: 2.4rem; }
}

/* ── Features ── */
.features-section {
  padding: 4rem 1.5rem;
  background: #0f1523;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: #151d2e;
  border: 1px solid #1e2d45;
  border-radius: 12px;
  padding: 1.8rem 1.5rem;
  transition: border-color 0.15s;
}
.feature-card:hover { border-color: #3b82f655; }

.feature-icon {
  font-size: 1.8rem;
  margin-bottom: 0.8rem;
}

.feature-card h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 0.6rem;
}

.feature-card p {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.6;
}

/* ── Nav cards ── */
.nav-cards-section {
  padding: 4rem 1.5rem;
  background: #0b0e17;
}

.section-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 1.5rem;
  text-align: center;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.nav-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.3rem;
  padding: 1.4rem 1.2rem;
  background: #111827;
  border: 1px solid #1e2d45;
  border-radius: 10px;
  text-decoration: none;
  transition: border-color 0.15s, background 0.15s;
}
.nav-card:hover {
  border-color: #3b82f6;
  background: #151d2e;
}

.nav-card--highlight {
  border-color: #92400e44;
  background: #1a1008;
}
.nav-card--highlight:hover {
  border-color: #f59e0b;
  background: #1f1408;
}

.nav-card-icon { font-size: 1.5rem; }
.nav-card-label { font-size: 0.95rem; font-weight: 700; color: #e2e8f0; }
.nav-card-desc  { font-size: 0.78rem; color: #64748b; line-height: 1.4; }

/* ── About band ── */
.about-band {
  padding: 2rem 1.5rem;
  background: #080b12;
  border-top: 1px solid #1e2d45;
  text-align: center;
}
.about-band p { font-size: 0.875rem; color: #475569; }
.about-band strong { color: #94a3b8; }
.about-band a { color: #3b82f6; text-decoration: none; }
.about-band a:hover { text-decoration: underline; }
</style>
