<template>
  <div class="stats-view">

    <section class="hero is-medium is-dark mb-0">
      <div class="hero-body has-text-centered">
        <p class="title mb-1">Statistics</p>
        <p class="subtitle is-6 has-text-grey-light" v-if="stats">
          Generated {{ formatAge(stats.generated_at) }}
        </p>
      </div>
    </section>

    <div v-if="loading" class="has-text-centered py-6">
      <span class="tag is-info is-medium">Loading statistics…</span>
    </div>

    <div v-else-if="error" class="notification is-danger mx-4 mt-4">{{ error }}</div>

    <template v-else-if="stats">

      <!-- Controls -->
      <div class="stats-controls">
        <div class="ctrl-group">
          <span class="ctrl-label">Period</span>
          <div class="btn-toggle">
            <button :class="['btn-t', period==='5year' && 'active']" @click="period='5year'">5Y</button>
            <button :class="['btn-t', period==='year'  && 'active']" @click="period='year'">Year</button>
            <button :class="['btn-t', period==='month' && 'active']" @click="period='month'">Month</button>
          </div>
        </div>
        <div class="ctrl-group">
          <span class="ctrl-label">Station</span>
          <select class="ctrl-select" v-model="station">
            <option value="all">All stations</option>
            <option v-for="s in allStations" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div class="ctrl-group">
          <span class="ctrl-label">Hourly</span>
          <div class="btn-toggle">
            <button :class="['btn-t', !normalized && 'active']" @click="normalized=false">Abs</button>
            <button :class="['btn-t', normalized  && 'active']" @click="normalized=true">Norm</button>
          </div>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="summary-row">
        <div class="s-card">
          <div class="s-value">{{ fmt(stats.summary.total_events) }}</div>
          <div class="s-label">Total events</div>
        </div>
        <div class="s-card">
          <div class="s-value">{{ fmt(stats.summary.total_multibolid) }}</div>
          <div class="s-label">Multi-station</div>
        </div>
        <div class="s-card">
          <div class="s-value">{{ activeStations }}</div>
          <div class="s-label">Active stations <span class="s-period">({{ periodLabel }})</span></div>
        </div>
        <div class="s-card">
          <div class="s-value">{{ stats.summary.avg_duration ? stats.summary.avg_duration.toFixed(2) + 's' : '—' }}</div>
          <div class="s-label">Avg duration</div>
        </div>
        <div class="s-card s-card--wide">
          <div class="s-value s-value--sm">{{ stats.summary.date_from ? stats.summary.date_from.slice(0,10) : '—' }}</div>
          <div class="s-label">First event</div>
        </div>
      </div>

      <!-- Daily / Weekly counts -->
      <div class="chart-card chart-card--full">
        <div class="chart-title">
          {{ period === '5year' ? 'Weekly event count — last 5 years' : period === 'year' ? 'Daily event count — last 365 days' : 'Daily event count — last 30 days' }}
        </div>
        <apexchart :key="`daily-${station}-${period}`" type="bar" height="220" :options="dailyOptions" :series="dailySeries" />
      </div>

      <!-- Row: Hourly + Station totals -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-title">Hourly profile (UTC) — {{ period === 'month' ? 'last month' : 'last year' }}{{ normalized ? ', normalized' : '' }}</div>
          <apexchart :key="`hourly-${station}-${period}-${normalized}`" type="bar" height="240" :options="hourlyOptions" :series="hourlySeries" />
        </div>
        <div class="chart-card">
          <div class="chart-title">Events per station (total)</div>
          <apexchart type="bar" height="240" :options="stationOptions" :series="stationSeries" />
        </div>
      </div>

      <!-- Annual profile: monthly bars + weekly line (folded across all years) -->
      <div class="chart-card chart-card--full">
        <div class="chart-title">
          Annual pattern — monthly (bars) &amp; weekly (line), normalized
          <span class="profile-note" v-if="stats.annual_profile.n_years">(avg of {{ stats.annual_profile.n_years }} years)</span>
        </div>
        <apexchart type="line" height="240" :options="annualOptions" :series="annualSeries" />
      </div>

      <!-- Row: Duration + Frequency histograms -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-title">Duration distribution (log scale)</div>
          <apexchart type="bar" height="220" :options="durationOptions" :series="durationSeries" />
        </div>
        <div class="chart-card">
          <div class="chart-title">Peak frequency distribution</div>
          <apexchart type="bar" height="220" :options="frequencyOptions" :series="frequencySeries" />
        </div>
      </div>

    </template>
  </div>
</template>

<script>
import axios from 'axios'

const DARK = {
  theme: { mode: 'dark' },
  chart: { background: '#0f1623', toolbar: { show: false }, animations: { enabled: false } },
  grid: { borderColor: '#1e2d45', strokeDashArray: 3 },
  xaxis: { labels: { style: { colors: '#64748b', fontSize: '11px' } }, axisBorder: { color: '#1e2d45' }, axisTicks: { color: '#1e2d45' } },
  yaxis: { labels: { style: { colors: '#64748b', fontSize: '11px' } } },
  tooltip: { theme: 'dark' },
  dataLabels: { enabled: false },
  legend: { labels: { colors: '#94a3b8' } },
}

// Approximate day-of-year at midpoint of each month (non-leap)
const MONTH_DOY_MID = [15, 46, 75, 105, 135, 166, 196, 227, 258, 288, 319, 349]
// Day-of-year at first day of each month
const MONTH_DOY_START = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

export default {
  name: 'StatsView',
  data() {
    return {
      stats: null,
      loading: true,
      error: null,
      period: 'year',
      station: 'all',
      normalized: false,
    }
  },
  mounted() {
    axios.get('/api/v1/stats/')
      .then(r => { this.stats = r.data; this.loading = false })
      .catch(e => { this.error = String(e); this.loading = false })
  },
  computed: {
    allStations() {
      if (!this.stats) return []
      return this.stats.station_totals.map(s => s.station)
    },

    activeStations() {
      if (!this.stats) return '—'
      if (this.period === '5year') return this.stats.summary.active_stations_5year
      if (this.period === 'month') return this.stats.summary.active_stations_month
      return this.stats.summary.active_stations_year
    },

    periodLabel() {
      if (this.period === '5year') return '5y'
      if (this.period === 'month') return '30d'
      return '1y'
    },

    // ── Daily / Weekly ─────────────────────────────────────────────────────────
    dailySeries() {
      if (!this.stats) return []
      if (this.period === '5year') {
        const { weekly_5y } = this.stats
        const data = this.station === 'all'
          ? weekly_5y.total
          : (weekly_5y.by_station[this.station] || weekly_5y.total.map(() => 0))
        return [{ name: 'Events', data }]
      }
      const { daily } = this.stats
      if (this.station === 'all') {
        return [{ name: 'Events', data: this.period === 'year' ? daily.total : daily.total.slice(-30) }]
      }
      const raw = daily.by_station[this.station] || daily.total.map(() => 0)
      return [{ name: this.station, data: this.period === 'year' ? raw : raw.slice(-30) }]
    },
    dailyOptions() {
      if (!this.stats) return DARK
      let categories
      if (this.period === '5year') categories = this.stats.weekly_5y.weeks
      else if (this.period === 'year') categories = this.stats.daily.dates
      else categories = this.stats.daily.dates.slice(-30)
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'daily' },
        xaxis: { ...DARK.xaxis, categories, tickAmount: this.period === 'month' ? 6 : 12 },
        colors: ['#3b82f6'],
        plotOptions: { bar: { columnWidth: '80%' } },
      }
    },

    // ── Hourly ─────────────────────────────────────────────────────────────────
    hourlySeries() {
      if (!this.stats) return []
      const src = this.period === 'month' ? this.stats.hourly_month : this.stats.hourly_year
      let raw = this.station === 'all'
        ? src.total
        : (src.by_station[this.station] || Array(24).fill(0))
      if (this.normalized) {
        const mx = Math.max(...raw) || 1
        raw = raw.map(v => +(v / mx).toFixed(3))
      }
      return [{ name: 'Count', data: raw }]
    },
    hourlyOptions() {
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'hourly' },
        xaxis: { ...DARK.xaxis, categories: Array.from({ length: 24 }, (_, i) => `${i}h`) },
        colors: ['#22d3ee'],
        plotOptions: { bar: { columnWidth: '70%' } },
      }
    },

    // ── Station totals ─────────────────────────────────────────────────────────
    stationSeries() {
      if (!this.stats) return []
      const sorted = [...this.stats.station_totals].sort((a, b) => b.count - a.count).slice(0, 20)
      return [{ name: 'Events', data: sorted.map(s => s.count) }]
    },
    stationOptions() {
      if (!this.stats) return DARK
      const sorted = [...this.stats.station_totals].sort((a, b) => b.count - a.count).slice(0, 20)
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'stations' },
        xaxis: { ...DARK.xaxis, categories: sorted.map(s => s.station) },
        colors: ['#f59e0b'],
        plotOptions: { bar: { columnWidth: '60%' } },
      }
    },

    // ── Annual profile: monthly bars + weekly line on day-of-year axis ─────────
    annualSeries() {
      if (!this.stats) return []
      const ap = this.stats.annual_profile
      const monthly = this.normalized ? ap.monthly_norm : ap.monthly_abs
      const weekly  = this.normalized ? ap.weekly_norm  : ap.weekly_abs

      const monthlyData = monthly.map((v, i) => ({ x: MONTH_DOY_MID[i], y: v }))
      const weeklyData  = weekly.map((v, i) => ({ x: Math.round((i + 0.5) * 7), y: v }))

      return [
        { name: this.normalized ? 'Monthly %'   : 'Monthly avg', type: 'bar',  data: monthlyData },
        { name: this.normalized ? 'Weekly %'    : 'Weekly avg',  type: 'line', data: weeklyData },
      ]
    },
    annualOptions() {
      const isNorm = this.normalized
      const labelFormatter = (val) => {
        const idx = MONTH_DOY_START.findIndex((d, i) =>
          val >= d && (i === 11 || val < MONTH_DOY_START[i + 1])
        )
        const nearStart = MONTH_DOY_START.some(d => Math.abs(val - d) <= 5)
        return nearStart && idx >= 0 ? MONTH_NAMES[idx] : ''
      }
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'annual', type: 'line' },
        stroke: { width: [0, 2], curve: 'smooth' },
        xaxis: {
          ...DARK.xaxis,
          type: 'numeric',
          min: 1,
          max: 365,
          tickAmount: 12,
          labels: { ...DARK.xaxis.labels, formatter: labelFormatter },
        },
        yaxis: {
          min: 0,
          labels: {
            style: { colors: '#64748b', fontSize: '11px' },
            formatter: v => isNorm ? v.toFixed(1) + '%' : Math.round(v).toLocaleString(),
          },
        },
        colors: ['#8b5cf6', '#22d3ee'],
        plotOptions: { bar: { columnWidth: '100%' } },
        tooltip: {
          theme: 'dark',
          x: {
            formatter: (val) => {
              const idx = MONTH_DOY_START.findIndex((d, i) => val >= d && (i === 11 || val < MONTH_DOY_START[i + 1]))
              return idx >= 0 ? MONTH_NAMES[idx] : `DOY ${val}`
            }
          },
          y: { formatter: v => isNorm ? v.toFixed(2) + '%' : Math.round(v).toLocaleString() },
        },
      }
    },

    // ── Histograms ─────────────────────────────────────────────────────────────
    durationSeries() {
      if (!this.stats) return []
      return [{ name: 'Count', data: this.stats.duration_hist.counts }]
    },
    durationOptions() {
      if (!this.stats) return DARK
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'duration' },
        xaxis: { ...DARK.xaxis, categories: this.stats.duration_hist.labels },
        yaxis: { ...DARK.yaxis, logarithmic: true, logBase: 10 },
        colors: ['#10b981'],
        plotOptions: { bar: { columnWidth: '90%' } },
      }
    },
    frequencySeries() {
      if (!this.stats) return []
      return [{ name: 'Count', data: this.stats.frequency_hist.counts }]
    },
    frequencyOptions() {
      if (!this.stats) return DARK
      return {
        ...DARK,
        chart: { ...DARK.chart, id: 'frequency' },
        xaxis: { ...DARK.xaxis, categories: this.stats.frequency_hist.labels },
        colors: ['#f43f5e'],
        plotOptions: { bar: { columnWidth: '90%' } },
      }
    },
  },
  methods: {
    fmt(n) { return n != null ? n.toLocaleString() : '—' },
    formatAge(iso) {
      const diff = Date.now() - new Date(iso).getTime()
      const h = Math.floor(diff / 3600000)
      if (h < 1) return 'just now'
      if (h < 24) return `${h}h ago`
      return `${Math.floor(h / 24)}d ago`
    },
  },
}
</script>

<style scoped>
.stats-view {
  background: #0b0e17;
  min-height: 100vh;
  padding-bottom: 3rem;
}

/* ── Controls ── */
.stats-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  background: #0f1623;
  border-bottom: 1px solid #1e2d45;
}

.ctrl-group {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.ctrl-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.btn-toggle {
  display: flex;
  border: 1px solid #2d4060;
  border-radius: 6px;
  overflow: hidden;
}

.btn-t {
  padding: 0.28em 0.9em;
  background: transparent;
  color: #64748b;
  border: none;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.12s, color 0.12s;
}
.btn-t.active { background: #1d4ed8; color: #fff; }
.btn-t:hover:not(.active) { background: #1e2d45; color: #cbd5e1; }

.ctrl-select {
  background: #0f1623;
  border: 1px solid #2d4060;
  border-radius: 6px;
  color: #cbd5e1;
  font-size: 0.82rem;
  padding: 0.28em 0.7em;
  cursor: pointer;
}

/* ── Summary cards ── */
.summary-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1px;
  background: #1e2d45;
  border-bottom: 1px solid #1e2d45;
}

.s-card {
  flex: 1 1 120px;
  background: #0f1623;
  padding: 1.2rem 1.5rem;
  text-align: center;
}

.s-card--wide { flex: 1 1 160px; }

.s-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: #e2e8f0;
  font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.s-value--sm { font-size: 1.2rem; }

.s-label {
  font-size: 0.72rem;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.3rem;
}

.s-period {
  font-weight: 400;
  text-transform: lowercase;
  letter-spacing: 0;
  color: #374151;
}

/* ── Charts ── */
.chart-card {
  background: #0f1623;
  border: 1px solid #1e2d45;
  border-radius: 10px;
  padding: 1rem 1rem 0.5rem;
  flex: 1 1 0;
  min-width: 0;
}

.chart-card--full {
  flex: 1 1 100%;
  margin: 1rem 1.5rem 0;
}

.chart-title {
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.5rem;
}

.profile-note {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
  color: #475569;
}

.chart-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 1rem;
  padding: 1rem 1.5rem 0;
}

@media (max-width: 600px) {
  .chart-row {
    flex-wrap: wrap;
  }
}
</style>
