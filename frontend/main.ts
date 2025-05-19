import './styles/tailwind.css'
import 'vite/modulepreload-polyfill'


import App from './App.vue'

import router from './router'
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faSearch, faMapMarkerAlt, faClock, faChevronRight, faBars, faTimes } from '@fortawesome/free-solid-svg-icons'
import { faTelegram, faVk, faWhatsapp, faOdnoklassniki } from '@fortawesome/free-brands-svg-icons'


library.add(
    faSearch,
    faMapMarkerAlt,
    faClock,
    faChevronRight,
    faBars,
    faTelegram,
    faVk,
    faWhatsapp,
    faOdnoklassniki,
    faTimes
)


const app = createApp(App)

app.use(createPinia())
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

app.mount('#app')
