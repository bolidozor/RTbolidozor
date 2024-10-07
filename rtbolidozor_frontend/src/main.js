import { createApp } from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import axios from 'axios'
import 'leaflet/dist/leaflet.css';

  // Google Analytics
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=G-E6LQWSNHVS';
  document.head.appendChild(script);

  script.onload = () => {
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'G-E6LQWSNHVS');
  };
  router.afterEach((to) => {
    gtag('config', 'G-E6LQWSNHVS', {
      'page_path': to.fullPath,
    });
  });

createApp(App).use(store).use(router).mount('#app')
