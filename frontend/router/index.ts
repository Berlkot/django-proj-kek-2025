import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import AdvertisementsPage from '../views/AdvertisementsPage.vue'
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import { useAuthStore } from '../stores/auth'; // Импортируем хранилище

// Определяем тип для маршрутов для лучшей типизации
const routes = [
  {
    path: '/',
    name: 'Home', // Рекомендуется использовать PascalCase для имен маршрутов
    component: HomePage,
  },
  {
    path: '/articles',
    name: 'Articles', // Имя маршрута для страницы статей
    component: ArticlesPage,
  },
  {
    path: '/article/:id(\\d+)', // :id должен быть числом
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetailPage.vue'), // Ленивая загрузка
    props: true, // Передаст :id как проп 'id' в компонент
  },
  {
    path: '/advertisements', // Или просто '/ads' как на макете
    name: 'Advertisements',
    component: AdvertisementsPage,
  },
  // Маршрут для детальной страницы объявления (пока заглушка)
  {
     path: '/advertisement/:id(\\d+)',
     name: 'AdvertisementDetail',
     component: () => import('../views/AdvertisementDetailPage.vue'), // Ленивая загрузка
     props: true
   },
  {
    path: '/rules',
    name: 'Rules',
    component: HomePage, // ЗАГЛУШКА
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: HomePage, // ЗАГЛУШКА
  },
  {
    path: '/post-ad', // Для кнопки "Разместить" в AppHeader
    name: 'PostAd',
    component: HomePage, // ЗАГЛУШКА
  },
  { path: '/login', name: 'Login', component: LoginPage, meta: { guestOnly: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { guestOnly: true } },
  {
    path: '/privacy',
    name: 'Privacy',
    component: HomePage, // ЗАГЛУШКА
  },
  {
    path: '/sitemap',
    name: 'Sitemap',
    component: HomePage, // ЗАГЛУШКА
  },
  {
    path: '/shelters',
    name: 'Shelters',
    component: HomePage, // ЗАГЛУШКА
  },
  // Добавьте NotFound страницу в конце
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundPage },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // всегда прокручивать наверх при навигации
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Навигационный страж (Navigation Guard)
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(); // Получаем доступ к хранилищу

  // Если маршрут требует аутентификации и пользователь не аутентифицирован
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { next: to.fullPath } }); // Перенаправляем на логин, сохраняя путь
  }
  // Если маршрут только для гостей (логин, регистрация) и пользователь аутентифицирован
  else if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'Home' }); // Перенаправляем на главную
  }
  // В остальных случаях разрешаем навигацию
  else {
    next();
  }
});

export default router
