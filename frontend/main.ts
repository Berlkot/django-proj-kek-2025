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
  faChevronDown, // faChevronDown для мобильных табов (если нужен будет аккордеон)
  faUser,
  faPhone,
  faEnvelope, // Для информации об авторе
  faPaw, // Для клейма/чипа (можно заменить)
  faCalendarAlt, // Для даты находки/потери
  faTag, // Для клички
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

// Инициализация состояния аутентификации ПОСЛЕ создания Pinia
const authStore = useAuthStore(); // Получаем экземпляр хранилища
authStore.initAuth().then(() => { // Вызываем initAuth для загрузки пользователя, если токен есть
    app.use(router); // Подключаем роутер после возможной асинхронной инициализации
    app.component('font-awesome-icon', FontAwesomeIcon);
    app.mount('#app');
}).catch(error => { // Обработка ошибок инициализации, если необходимо
    console.error("Auth initialization failed:", error);
    // Можно показать пользователю сообщение об ошибке или выполнить другие действия
    // Важно все равно смонтировать приложение
    app.use(router);
    app.component('font-awesome-icon', FontAwesomeIcon);
    app.mount('#app');
});
