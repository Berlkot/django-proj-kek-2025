import './styles/tailwind.css'
import 'vite/modulepreload-polyfill'

import App from './App.vue'
import { useAuthStore } from './stores/auth'

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
  faTrashAlt,
  faHeart,
  faStar,
} from '@fortawesome/free-solid-svg-icons'
import { faTelegram, faVk, faWhatsapp, faOdnoklassniki } from '@fortawesome/free-brands-svg-icons'
import * as Sentry from '@sentry/vue'
import { faG } from '@fortawesome/free-solid-svg-icons/faG'
import { faGoogle } from '@fortawesome/free-brands-svg-icons/faGoogle'

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
  faGoogle,
  faWhatsapp,
  faOdnoklassniki,
  faPencilAlt,
  faTrashAlt,
  faHeart,
  faStar,
)
const app = createApp(App)

app.use(createPinia())

Sentry.init({
  app,
  dsn: 'https://b8f76648080391f01c648c50fc87ccce@o4509505207009280.ingest.de.sentry.io/4509505248362576',
  integrations: [
    Sentry.browserTracingIntegration({ router }),
    Sentry.replayIntegration({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  tracesSampleRate: 1.0,

  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  environment: import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development',
})

const authStore = useAuthStore()
authStore
  .initAuth()
  .then(() => {
    app.use(router)
    app.component('font-awesome-icon', FontAwesomeIcon)
    app.mount('#app')
  })
  .catch((error) => {
    console.error('Auth initialization failed:', error)

    app.use(router)
    app.component('font-awesome-icon', FontAwesomeIcon)
    app.mount('#app')
  })
