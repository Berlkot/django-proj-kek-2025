import './styles/tailwind.css'
import 'vite/modulepreload-polyfill'

import App from './App.vue'
import { useAuthStore } from './stores/auth';

import router from './router'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faSearch,
  faMapMarkerAlt,
  faClock,
  faChevronRight,
  faBars,
  faTimes,
  faChevronLeft,
  faChevronDown,
  faUser,
  faPhone,
  faEnvelope,
  faPaw,
  faCalendarAlt,
  faTag,
  faVenusMars,
  faFilter,
  faPencilAlt,
  faTrashAlt
} from '@fortawesome/free-solid-svg-icons'
import { faTelegram, faVk, faWhatsapp, faOdnoklassniki } from '@fortawesome/free-brands-svg-icons'

library.add(
  faSearch,
  faMapMarkerAlt,
  faClock,
  faChevronRight,
  faBars,
  faTimes,
  faFilter,
  faChevronLeft,
  faChevronDown,
  faUser,
  faPhone,
  faEnvelope,
  faPaw,
  faCalendarAlt,
  faTag,
  faVenusMars,
  faTelegram,
  faVk,
  faWhatsapp,
  faOdnoklassniki,
  faPencilAlt,
  faTrashAlt
)
const app = createApp(App)

app.use(createPinia())


const authStore = useAuthStore();
authStore.initAuth().then(() => {
    app.use(router);
    app.component('font-awesome-icon', FontAwesomeIcon);
    app.mount('#app');
}).catch(error => {
    console.error("Auth initialization failed:", error);


    app.use(router);
    app.component('font-awesome-icon', FontAwesomeIcon);
    app.mount('#app');
});
