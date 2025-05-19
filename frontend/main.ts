import './styles/tailwind.css'
import 'vite/modulepreload-polyfill'

import App from './App.vue'

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
  faChevronDown, // faChevronDown для мобильных табов (если нужен будет аккордеон)
  faUser,
  faPhone,
  faEnvelope, // Для информации об авторе
  faPaw, // Для клейма/чипа (можно заменить)
  faCalendarAlt, // Для даты находки/потери
  faTag, // Для клички
  faVenusMars,
  faFilter,
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
  faOdnoklassniki
)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
