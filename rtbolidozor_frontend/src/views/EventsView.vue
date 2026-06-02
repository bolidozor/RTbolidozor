<template>
  <div class="events-view">
    <section class="hero is-medium is-dark mb-6">
      <div class="hero-body has-text-centered">
        <p class="title mb-2">Event Browser</p>
      </div>
    </section>

    <div class="box controls-box">
      <div class="field is-grouped is-grouped-multiline is-align-items-flex-end">
        <div class="control">
          <label class="label is-small">From</label>
          <input class="input" type="datetime-local" v-model="fromDate" />
        </div>
        <div class="control">
          <label class="label is-small">To</label>
          <input class="input" type="datetime-local" v-model="toDate" />
        </div>
        <div class="control">
          <label class="label is-small">&nbsp;</label>
          <button class="button is-primary" @click="applyWindow">Apply</button>
        </div>
        <div class="control">
          <label class="label is-small">&nbsp;</label>
          <div class="buttons has-addons">
            <button class="button" @click="shiftWindow(-windowHours / 2)" title="Shift back">←</button>
            <button class="button" @click="shiftWindow(+windowHours / 2)" title="Shift forward">→</button>
          </div>
        </div>
        <div class="control">
          <label class="label is-small">Window</label>
          <div class="buttons has-addons">
            <button
              v-for="opt in windowOptions"
              :key="opt.h"
              class="button is-small"
              :class="{ 'is-info is-selected': windowHours === opt.h }"
              @click="setWindowSize(opt.h)"
            >{{ opt.label }}</button>
          </div>
        </div>
        <div class="control">
          <label class="label is-small">Selection</label>
          <div class="buttons has-addons">
            <button
              class="button is-small"
              :class="{ 'is-dark is-selected': !multiMode }"
              @click="setMode(false)"
            >Single</button>
            <button
              class="button is-small"
              :class="{ 'is-dark is-selected': multiMode }"
              @click="setMode(true)"
            >Multi</button>
          </div>
        </div>
        <div class="control">
          <label class="label is-small">Viewer</label>
          <div class="buttons has-addons">
            <button
              class="button is-small"
              :class="{ 'is-dark is-selected': viewer === 'htfits' }"
              @click="setViewer('htfits')"
            >htfits</button>
            <button
              class="button is-small"
              :class="{ 'is-dark is-selected': viewer === 'js9' }"
              @click="setViewer('js9')"
            >JS9</button>
          </div>
        </div>
        <div class="control">
          <label class="label is-small">&nbsp;</label>
          <span class="tag is-light is-medium" v-if="!loading">
            {{ events.length }} events, {{ timelineRows.length }} stations
          </span>
          <span class="tag is-info is-medium" v-else>Loading…</span>
        </div>
      </div>
    </div>

    <div v-if="error" class="notification is-danger mx-4">{{ error }}</div>

    <div class="box timeline-box mx-4" v-if="timelineRows.length > 0" :class="{ 'is-loading-overlay': loading }">
      <div v-if="loading" class="loading-banner">Loading…</div>
      <div class="timeline-axis-top">
        <div class="timeline-label-spacer"></div>
        <div class="timeline-ticks">
          <span
            v-for="tick in axisTicks"
            :key="tick.pct"
            class="timeline-tick"
            :style="{ left: tick.pct + '%' }"
          >{{ tick.label }}</span>
        </div>
      </div>

      <div
        v-for="row in timelineRows"
        :key="row.station.identifier"
        class="timeline-row"
      >
        <div class="timeline-label" :title="row.station.identifier">
          {{ row.station.name }}
        </div>
        <div class="timeline-track">
          <span
            v-for="ev in row.events"
            :key="ev.id"
            class="event-dot"
            :class="{ 'is-selected': isSelected(ev) }"
            :style="{ left: ev.pct + '%', width: ev.size + 'px', height: ev.size + 'px' }"
            :title="formatTime(ev.corrected_start_time || ev.obs_start_time)"
            @click="selectEvent(ev)"
          ></span>
          <span
            v-for="mb in multibolidPcts"
            :key="'mb-' + mb.id"
            class="multibolid-line"
            :style="{ left: mb.pct + '%' }"
            :title="'Multibolid: ' + formatTime(mb.timestamp)"
          ></span>
        </div>
      </div>
    </div>

    <div v-if="!loading && timelineRows.length === 0 && !error" class="notification is-warning mx-4">
      No events in selected time window.
    </div>
    <div v-if="loading && timelineRows.length === 0" class="notification is-info mx-4">
      Loading…
    </div>

    <div
      v-for="item in selectedItems"
      :key="item.event.id"
      class="box event-detail mx-4 mt-4"
    >
      <button class="delete is-pulled-right" @click="removeItem(item.event.id)"></button>
      <h3 class="title is-5 mb-3">Event detail</h3>
      <div class="columns is-vcentered is-multiline">
        <div class="column is-narrow">
          <table class="table is-narrow detail-table">
            <tbody>
              <tr>
                <th>ID</th>
                <td><code>{{ item.event.met_file ? item.event.met_file.name.replace(/_met\.fits$/, '') : item.event.id }}</code></td>
              </tr>
              <tr>
                <th>Station</th>
                <td>{{ item.event.station.name }} <span class="tag is-light ml-1">{{ item.event.station.identifier }}</span></td>
              </tr>
              <tr>
                <th>Observed start</th>
                <td>{{ formatTime(item.event.obs_start_time) }}</td>
              </tr>
              <tr v-if="item.event.corrected_start_time">
                <th>Corrected start</th>
                <td>{{ formatTime(item.event.corrected_start_time) }}</td>
              </tr>
              <tr>
                <th>Duration</th>
                <td>{{ item.event.duration != null ? item.event.duration.toFixed(3) + ' s' : '—' }}</td>
              </tr>
              <tr>
                <th>Peak frequency</th>
                <td>{{ item.event.peak_frequency != null ? item.event.peak_frequency.toFixed(1) + ' Hz' : '—' }}</td>
              </tr>
              <tr>
                <th>Magnitude</th>
                <td>{{ item.event.magnitude != null ? item.event.magnitude.toFixed(3) : '—' }}</td>
              </tr>
            </tbody>
          </table>
          <div class="buttons mt-2">
            <a v-if="item.event.met_file" :href="item.event.met_file.link" class="button is-link is-small" target="_blank">MET file</a>
            <a v-if="item.event.raw_file" :href="item.event.raw_file.link" class="button is-link is-small" target="_blank">RAW file</a>
            <router-link :to="{ path: '/snapView', query: { time: snapViewTime(item.event) } }" class="button is-info is-small" target="_blank">SnapView</router-link>
          </div>
        </div>
        <div class="column preview-column">
          <div class="preview-area">
            <template v-if="viewer === 'htfits'">
              <img
                v-if="item.event.met_file"
                :src="`https://rtbolidozor.astro.cz/f.png?${item.event.met_file.link}`"
                alt="Event preview"
                class="preview-img"
              />
            </template>
            <template v-else-if="viewer === 'js9'">
              <div
                v-if="item.event.met_file"
                :id="'js9-met-' + item.event.id"
                class="JS9"
                style="width:100%;height:340px;"
              ></div>
            </template>
          </div>
        </div>
        <div class="column preview-column">
          <div class="preview-area">
            <template v-if="viewer === 'htfits'">
              <img
                v-if="item.snapshot"
                :src="`https://rtbolidozor.astro.cz/f.png?${item.snapshot.snap_file.link}`"
                alt="Snapshot"
                class="preview-img"
              />
              <span v-else-if="item.snapshotLoading" class="tag is-info">Loading…</span>
              <span v-else class="tag is-light">No snapshot</span>
            </template>
            <template v-else-if="viewer === 'js9'">
              <div
                v-if="item.snapshot"
                :id="'js9-snap-' + item.event.id"
                class="JS9"
                style="width:100%;height:340px;"
              ></div>
              <span v-else-if="item.snapshotLoading" class="tag is-info">Loading…</span>
              <span v-else class="tag is-light">No snapshot</span>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EventsView',
  data() {
    return {
      events: [],
      multibolids: [],
      selectedItems: [],
      multiMode: false,
      viewer: 'htfits',
      windowHours: 1,
      windowOptions: [
        { h: 0.5, label: '30m' },
        { h: 1,   label: '1h' },
        { h: 6,   label: '6h' },
      ],
      fromDate: '',
      toDate: '',
      preselectIds: [],
      loading: false,
      error: null,
    }
  },
  computed: {
    windowStart() {
      return this.fromDate ? new Date(this.fromDate + 'Z') : null
    },
    windowEnd() {
      return this.toDate ? new Date(this.toDate + 'Z') : null
    },
    windowMs() {
      if (!this.windowStart || !this.windowEnd) return 1
      return this.windowEnd - this.windowStart
    },
    timelineRows() {
      const stationMap = {}
      for (const ev of this.events) {
        const id = ev.station.identifier
        if (!stationMap[id]) {
          stationMap[id] = { station: ev.station, events: [] }
        }
        const t = new Date(ev.corrected_start_time || ev.obs_start_time)
        const pct = ((t - this.windowStart) / this.windowMs) * 100
        const dur = ev.duration || 0
        const size = Math.min(28, Math.max(6, 6 + dur * 8))
        stationMap[id].events.push({ ...ev, pct: Math.max(0, Math.min(100, pct)), size })
      }
      return Object.values(stationMap).sort((a, b) =>
        a.station.name.localeCompare(b.station.name)
      )
    },
    multibolidPcts() {
      if (!this.windowStart || !this.windowMs) return []
      return this.multibolids.map(mb => {
        const t = new Date(mb.timestamp)
        const pct = ((t - this.windowStart) / this.windowMs) * 100
        return { id: mb.id, pct: Math.max(0, Math.min(100, pct)), timestamp: mb.timestamp }
      })
    },
    axisTicks() {
      if (!this.windowStart || !this.windowEnd) return []
      const ticks = []
      for (let i = 0; i <= 4; i++) {
        const pct = i * 25
        const t = new Date(this.windowStart.getTime() + (this.windowMs * pct) / 100)
        ticks.push({ pct, label: this.formatAxisTime(t) })
      }
      return ticks
    },
  },
  watch: {
    fromDate(newVal) {
      if (!newVal) return
      const from = new Date(newVal + 'Z')
      const to = new Date(this.toDate + 'Z')
      if (isNaN(to) || to <= from) {
        this.toDate = new Date(from.getTime() + this.windowHours * 60 * 60 * 1000)
          .toISOString().slice(0, 16)
      }
    },
    selectedItems(items) {
      this.syncUrl(items)
    },
  },
  mounted() {
    this.initTimeWindow()
    this.syncUrl()
    this.fetchEvents()
  },
  methods: {
    initTimeWindow() {
      const params = new URLSearchParams(window.location.search)
      if (params.get('selected')) {
        this.preselectIds = params.get('selected').split(',').filter(Boolean)
        this.multiMode = this.preselectIds.length > 1
      }
      if (params.get('from') && params.get('to')) {
        this.fromDate = params.get('from').slice(0, 16)
        this.toDate = params.get('to').slice(0, 16)
      } else {
        const now = new Date()
        const to = new Date(now.getTime() - 2 * 60 * 60 * 1000)
        const from = new Date(to.getTime() - this.windowHours * 60 * 60 * 1000)
        this.toDate = to.toISOString().slice(0, 16)
        this.fromDate = from.toISOString().slice(0, 16)
      }
    },
    fetchEvents() {
      this.loading = true
      this.error = null
      this.selectedItems = []
      const params = {
        from: new Date(this.fromDate + 'Z').toISOString(),
        to:   new Date(this.toDate   + 'Z').toISOString(),
        page_size: 1000,
      }
      Promise.all([
        axios.get('/api/v1/events/', { params }),
        axios.get('/api/v1/multiStationEvent/', { params: { ...params, page_size: 500 } }),
      ]).then(([evRes, mbRes]) => {
        this.events = evRes.data.results
        this.multibolids = mbRes.data.results
        this.loading = false
        if (this.preselectIds.length) {
          const toSelect = this.events.filter(e => this.preselectIds.includes(String(e.id)))
          toSelect.forEach(ev => this.selectEvent(ev))
          this.preselectIds = []
        }
      }).catch(err => {
        this.error = String(err)
        this.loading = false
      })
    },
    syncUrl(items) {
      const sel = (items ?? this.selectedItems).map(i => i.event.id).join(',')
      const params = new URLSearchParams()
      if (this.fromDate) params.set('from', this.fromDate)
      if (this.toDate)   params.set('to',   this.toDate)
      if (sel)           params.set('selected', sel)
      window.history.replaceState(null, '', `${window.location.pathname}?${params}`)
    },
    applyWindow() {
      this.syncUrl([])
      this.fetchEvents()
    },
    shiftWindow(hours) {
      const delta = hours * 60 * 60 * 1000
      this.fromDate = new Date(new Date(this.fromDate + 'Z').getTime() + delta).toISOString().slice(0, 16)
      this.toDate   = new Date(new Date(this.toDate   + 'Z').getTime() + delta).toISOString().slice(0, 16)
      this.applyWindow()
    },
    setWindowSize(hours) {
      this.windowHours = hours
      const from = new Date(this.fromDate + 'Z')
      const newTo = new Date(from.getTime() + hours * 60 * 60 * 1000)
      this.toDate = newTo.toISOString().slice(0, 16)
      this.applyWindow()
    },
    setMode(multi) {
      this.multiMode = multi
      this.selectedItems = []
    },
    setViewer(v) {
      this.viewer = v
      if (v === 'js9') {
        this.$nextTick(() => {
          this.selectedItems.forEach(item => this.loadJS9(item))
        })
      }
    },
    fitsProxyUrl(link) {
      return `/api/v1/fits/?url=${encodeURIComponent(link)}`
    },
    loadJS9(item) {
      if (!window.JS9) return
      const onload = function() { window.JS9.SetColormap('b', { display: this.display }) }
      if (item.event.met_file) {
        const id = 'js9-met-' + item.event.id
        window.JS9.AddDivs(id)
        window.JS9.Load(this.fitsProxyUrl(item.event.met_file.link), { display: id, onload })
      }
      if (item.snapshot) {
        const id = 'js9-snap-' + item.event.id
        window.JS9.AddDivs(id)
        window.JS9.Load(this.fitsProxyUrl(item.snapshot.snap_file.link), { display: id, onload })
      }
    },
    isSelected(ev) {
      return this.selectedItems.some(i => i.event.id === ev.id)
    },
    selectEvent(ev) {
      if (this.isSelected(ev)) {
        this.removeItem(ev.id)
        return
      }
      const item = { event: ev, snapshot: null, snapshotLoading: true }
      if (this.multiMode) {
        this.selectedItems = [...this.selectedItems, item]
      } else {
        this.selectedItems = [item]
      }
      if (this.viewer === 'js9') {
        this.$nextTick(() => this.loadJS9(item))
      }
      const t = new Date(ev.corrected_start_time || ev.obs_start_time)
      const ts = t.toISOString().slice(0, 19).replace(/[:\-]/g, '')
      axios.get(`/api/v1/snapshots/${ts}/`)
        .then(response => {
          const stationData = response.data.find(
            s => s.station_info.identifier === ev.station.identifier
          )
          const found = this.selectedItems.find(i => i.event.id === ev.id)
          if (found) {
            found.snapshot = stationData?.snapshots?.[0] ?? null
            found.snapshotLoading = false
            if (this.viewer === 'js9' && found.snapshot) {
              this.$nextTick(() => this.loadJS9(found))
            }
          }
        })
        .catch(() => {
          const found = this.selectedItems.find(i => i.event.id === ev.id)
          if (found) found.snapshotLoading = false
        })
    },
    removeItem(eventId) {
      this.selectedItems = this.selectedItems.filter(i => i.event.id !== eventId)
    },
    formatTime(isoStr) {
      if (!isoStr) return '—'
      return new Date(isoStr).toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
    },
    formatAxisTime(date) {
      return date.toISOString().replace('T', ' ').slice(5, 16)
    },
    snapViewTime(event) {
      const t = event.corrected_start_time || event.obs_start_time
      return t.slice(0, 19)
    },
  },
}
</script>

<style scoped>
.events-view {
  background: #0b0e17;
  min-height: 100vh;
  padding-bottom: 3rem;
}

.controls-box {
  margin: 0 1rem 1rem;
}

.is-loading-overlay {
  opacity: 0.45;
  pointer-events: none;
  position: relative;
}

.loading-banner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(15,22,35,0.9);
  padding: 0.35em 1em;
  border-radius: 4px;
  font-weight: 600;
  color: #94a3b8;
  z-index: 1;
  pointer-events: none;
}

.timeline-box {
  overflow-x: auto;
  padding: 0.75rem 1rem;
  background: #0f1623;
  border-color: #1e2d45;
}

.timeline-axis-top {
  display: flex;
  align-items: flex-end;
  margin-bottom: 4px;
}

.timeline-label-spacer {
  width: 160px;
  flex-shrink: 0;
}

.timeline-ticks {
  position: relative;
  flex: 1;
  height: 20px;
  font-size: 0.72rem;
  color: #475569;
}

.timeline-tick {
  position: absolute;
  transform: translateX(-50%);
  white-space: nowrap;
}

.timeline-row {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  min-height: 28px;
}

.timeline-label {
  width: 160px;
  flex-shrink: 0;
  font-size: 0.82rem;
  font-weight: 600;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 8px;
}

.timeline-track {
  position: relative;
  flex: 1;
  height: 24px;
  background: #1e2d45;
  border-radius: 4px;
}

.event-dot {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: background 0.1s, opacity 0.1s;
}

.event-dot:hover {
  background: #60a5fa;
  opacity: 0.9;
}

.event-dot.is-selected {
  background: #f43f5e;
}

.multibolid-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 100, 0, 0.75);
  pointer-events: none;
  transform: translateX(-50%);
  z-index: 1;
}

.event-detail {
  margin-bottom: 1rem;
  background: #0f1623;
  border-color: #1e2d45;
}

.detail-table { background: transparent !important; }
.detail-table th {
  color: #64748b;
  border-color: #1e2d45 !important;
  font-weight: 600;
  white-space: nowrap;
}
.detail-table td {
  color: #e2e8f0;
  border-color: #1e2d45 !important;
}
.detail-table code {
  background: #1e2d45;
  color: #94a3b8;
  font-size: 0.78rem;
}

.preview-column {
  min-width: 320px;
  flex: 1;
}

.preview-area {
  height: 340px;
  display: flex;
  align-items: flex-start;
  overflow: visible;
}

.preview-img {
  max-width: 100%;
  max-height: 340px;
  height: auto;
  display: block;
}
</style>
