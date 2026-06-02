import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import StationsView from '../views/StationsView.vue'
import MapView from '../views/MapView.vue'
import SnapView from '../views/SnapView.vue'
import MultiBolidView from '../views/MultiBolidView.vue'
import ContactView from '../views/ContactView.vue'
import EventsView from '../views/EventsView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  { 
    path: '/stations',
    name: 'stations',
    component: StationsView
  },
  {
    path: '/multibolid',
    name: 'multibolid',
    component: MultiBolidView
  },
  {
    path: '/snapView',
    name: 'snapView',
    component: SnapView
  },
  {
    path: '/map',
    name: '/map',
    component: MapView
  },
  {
    path: '/realtime',
    redirect: '/map'
  },
  {
    path: '/events',
    name: 'events',
    component: EventsView
  },
  {
    path: '/stats',
    name: 'stats',
    component: () => import('../views/StatsView.vue')
  },
  { path: '/contact',
    name: 'contact',
    component: ContactView

  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
