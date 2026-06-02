<template>
  <div class="multibolid-view">

    <section class="hero is-medium is-dark mb-5">
      <div class="hero-body has-text-centered">
        <p class="title mb-1">Multi-station Events</p>
        <p class="subtitle is-6 has-text-grey-light">Meteors detected simultaneously by multiple stations</p>
      </div>
    </section>

    <div class="mb-page">

      <!-- Pagination top -->
      <div v-if="!singleId" class="pagination-bar pagination-bar--top">
        <button class="mb-btn" :disabled="!previous" @click="goToPage(previous)">← Previous</button>
        <span class="pagination-info">Page {{ current }}</span>
        <button class="mb-btn" :disabled="!next" @click="goToPage(next)">Next →</button>
      </div>

      <div v-if="singleId && groups.length === 0" class="notification is-warning mx-4">
        Multibolid not found.
      </div>

      <div v-for="group in groups" :key="group.id" class="mb-card">

        <!-- Header -->
        <div class="mb-header">
          <div class="mb-time">
            <span class="mb-date">{{ formatDate(group.timestamp) }}</span>
            <span class="mb-clock">{{ formatTime(group.timestamp) }} UTC</span>
          </div>
          <div class="mb-meta">
            <span class="mb-badge">{{ group.events.length }} station{{ group.events.length > 1 ? 's' : '' }}</span>
          </div>
          <div class="mb-actions">
            <a :href="permalinkHref(group)" class="mb-btn" title="Permalink">🔗</a>
            <button class="mb-btn" @click="toggleZoom(group.id)" :title="zoomGroups[group.id] ? 'Normal view' : 'Zoom'">
              {{ zoomGroups[group.id] ? '⊟' : '⊞' }}
            </button>
            <a :href="`/SnapView?time=${group.timestamp.slice(0, -1)}`" target="_blank" class="mb-btn">SnapView</a>
            <router-link :to="eventsLink(group)" class="mb-btn mb-btn--primary">Events →</router-link>
          </div>
        </div>

        <!-- Images -->
        <div class="mb-images" :class="{ 'mb-images--zoom': zoomGroups[group.id] }">
          <div v-for="event in group.events" :key="event.id" class="mb-image-card">
            <img
              :src="`https://rtbolidozor.astro.cz/f.png?${event.met_file.link}`"
              :alt="event.station.name"
              class="mb-image"
            />
            <div class="mb-image-label">
              <span class="mb-station-name">{{ event.station.name }}</span>
              <span class="mb-duration" v-if="event.duration">{{ event.duration.toFixed(2) }}s</span>
            </div>
          </div>
        </div>

        <!-- Collapsible table -->
        <div class="mb-details">
          <button class="mb-toggle" @click="toggleTable(group.id)">
            {{ openTables[group.id] ? '▲ Hide details' : '▼ Show details' }}
          </button>
          <div v-if="openTables[group.id]" class="mb-table-wrap">
            <table class="table is-narrow is-fullwidth mt-2">
              <thead>
                <tr>
                  <th>Station</th>
                  <th>Start time</th>
                  <th>Duration</th>
                  <th>Files</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="event in group.events" :key="event.id">
                  <td>{{ event.station.name }}</td>
                  <td>{{ event.obs_start_time }}</td>
                  <td>{{ event.duration ? event.duration.toFixed(3) + ' s' : '—' }}</td>
                  <td>
                    <a v-if="event.met_file" :href="event.met_file.link" class="tag is-link is-light mr-1" target="_blank">met</a>
                    <a v-if="event.raw_file" :href="event.raw_file.link" class="tag is-link is-light" target="_blank">raw</a>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- Pagination (hidden when viewing single) -->
      <div v-if="!singleId" class="pagination-bar">
        <button class="mb-btn" :disabled="!previous" @click="goToPage(previous)">← Previous</button>
        <span class="pagination-info">Page {{ current }}</span>
        <button class="mb-btn" :disabled="!next" @click="goToPage(next)">Next →</button>
      </div>
      <div v-else class="pagination-bar">
        <router-link to="/multibolid" class="mb-btn">← All events</router-link>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'MultiBolidView',
  data() {
    return {
      groups: [],
      next: null,
      previous: null,
      current: 1,
      openTables: {},
      zoomGroups: {},
      singleId: null,
    }
  },
  mounted() {
    const params = new URLSearchParams(window.location.search)
    const id = params.get('id')
    if (id) {
      this.singleId = id
      this.getGroups(`/api/v1/multiStationEvent/?id=${id}`)
    } else {
      this.getGroups('/api/v1/multiStationEvent/')
    }
  },
  methods: {
    getGroups(url) {
      axios.get(url)
        .then(response => {
          this.groups = response.data.results
          this.next     = response.data.next     ? response.data.next.replace('http://', 'https://')     : null
          this.previous = response.data.previous ? response.data.previous.replace('http://', 'https://') : null
          this.openTables = {}
        })
        .catch(error => console.log(error))
    },
    goToPage(url) {
      if (url) {
        const urlParams = new URLSearchParams(url.split('?')[1])
        this.current = urlParams.get('page') || 1
        this.getGroups(url)
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    toggleTable(id) {
      this.openTables = { ...this.openTables, [id]: !this.openTables[id] }
    },
    toggleZoom(id) {
      this.zoomGroups = { ...this.zoomGroups, [id]: !this.zoomGroups[id] }
    },
    permalinkHref(group) {
      return `/multibolid?id=${group.id}`
    },
    eventsLink(group) {
      const times = group.events.map(e => new Date(e.obs_start_time).getTime())
      const minT = Math.min(...times)
      const maxT = Math.max(...times)
      const pad  = 5 * 60 * 1000
      const from = new Date(minT - pad).toISOString().slice(0, 16)
      const to   = new Date(maxT + pad).toISOString().slice(0, 16)
      const ids  = group.events.map(e => e.id).join(',')
      return `/events?from=${from}&to=${to}&selected=${ids}`
    },
    formatDate(iso) {
      return new Date(iso).toISOString().slice(0, 10)
    },
    formatTime(iso) {
      return new Date(iso).toISOString().slice(11, 19)
    },
  },
}
</script>

<style scoped>
.multibolid-view {
  background: #0b0e17;
  min-height: 100vh;
  color: #e0e6f0;
}

.mb-page {
  padding: 0 1rem 3rem;
}

/* ── Card ── */
.mb-card {
  background: #111827;
  border: 1px solid #1e2d45;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  overflow: hidden;
}

/* ── Header ── */
.mb-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  border-bottom: 1px solid #1e2d45;
  flex-wrap: wrap;
}

.mb-time {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  flex: 1;
}

.mb-date {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e2e8f0;
}

.mb-clock {
  font-size: 1.4rem;
  font-weight: 800;
  color: #22d3ee;
  font-variant-numeric: tabular-nums;
}

.mb-meta {
  display: flex;
  align-items: center;
}

.mb-badge {
  font-size: 0.75rem;
  color: #64748b;
  background: #1e2d45;
  border-radius: 20px;
  padding: 0.2em 0.8em;
}

.mb-actions {
  display: flex;
  gap: 0.5rem;
}

.mb-btn {
  display: inline-block;
  padding: 0.35em 0.9em;
  background: #1e2d45;
  color: #cbd5e1;
  border: 1px solid #2d4060;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.12s, color 0.12s;
  white-space: nowrap;
}
.mb-btn:hover:not([disabled]) { background: #263550; color: #fff; }
.mb-btn[disabled] { opacity: 0.4; cursor: default; pointer-events: none; }

.mb-btn--primary {
  background: #1d4ed8;
  border-color: #2563eb;
  color: #fff;
}
.mb-btn--primary:hover { background: #2563eb; }

/* ── Images ── */
.mb-images {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 8px;
  background: #0d1420;
  padding: 1rem 1rem 0.75rem;
  scroll-snap-type: x mandatory;
}

.mb-images .mb-image-card {
  flex: 0 0 calc(100% / 3.5);
  scroll-snap-align: start;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* Zoom mode — 90vw per image */
.mb-images--zoom .mb-image-card {
  flex: 0 0 90vw;
}

.mb-image {
  display: block;
  width: 100%;
  height: auto;
  max-height: 320px;
  object-fit: contain;
  border-radius: 4px;
  background: #000;
}

.mb-images--zoom .mb-image {
  max-height: 70vh;
}

.mb-image-label {
  display: flex;
  justify-content: space-between;
  padding: 0.3rem 0.1rem 0.1rem;
}

.mb-station-name {
  font-size: 0.78rem;
  font-weight: 600;
  color: #94a3b8;
}

.mb-duration {
  font-size: 0.75rem;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

/* ── Details ── */
.mb-details {
  padding: 0.5rem 1.2rem 0.8rem;
  border-top: 1px solid #1a2540;
}

.mb-toggle {
  background: none;
  border: none;
  color: #475569;
  font-size: 0.78rem;
  cursor: pointer;
  padding: 0;
}
.mb-toggle:hover { color: #94a3b8; }

.mb-table-wrap { overflow-x: auto; }
.mb-table-wrap .table {
  background: #0d1420 !important;
  color: #94a3b8;
  font-size: 0.82rem;
}
.mb-table-wrap .table th {
  color: #64748b;
  border-color: #1e2d45 !important;
  background: #0d1420 !important;
}
.mb-table-wrap .table td { border-color: #1e2d45 !important; }
.mb-table-wrap .table tr:hover td { background: #111827 !important; }

/* ── Pagination ── */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 1rem 0 2rem;
}

.pagination-bar--top {
  padding: 0 0 1rem;
}

.pagination-info {
  font-size: 0.85rem;
  color: #475569;
}
</style>
