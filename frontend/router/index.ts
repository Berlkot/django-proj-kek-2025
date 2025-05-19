import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import AdvertisementsPage from '../views/AdvertisementsPage.vue'
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import ArticleEditPage from '../views/ArticleEditPage.vue';
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
    path: '/articles/edit/:id(\\d+)', // Маршрут для редактирования существующей статьи
    name: 'ArticleEdit',
    component: ArticleEditPage,
    props: true, // Передаст :id как проп
    meta: { requiresAuth: true, requiresModeratorOrAdmin: true } // Защита маршрута
  },
  {
    path: '/articles/create', // Маршрут для создания новой статьи
    name: 'ArticleCreate',
    component: ArticleEditPage, // Используем тот же компонент, но без id
    meta: { requiresAuth: true, requiresModeratorOrAdmin: true }
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
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { next: to.fullPath } });
  } else if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'Home' });
  } else if (to.meta.requiresModeratorOrAdmin) {
    // Проверяем, есть ли пользователь и является ли он админом или имеет роль с правом создавать/редактировать статьи
    // Эта проверка может быть более сложной в зависимости от того, как вы храните права роли.
    // Для примера, предположим, что is_staff или определенная роль дают доступ.
    // В идеале, у authStore.user должна быть информация о роли и ее правах.
    const user = authStore.user;
    // Простая проверка: является ли админом ИЛИ (если есть роль и поле can_edit_any_article/can_create_article)
    // Для большей точности, на бэкенде эндпоинт редактирования/создания статьи вернет 403, если прав нет.
    // Здесь мы можем сделать предварительную проверку, чтобы не пускать на страницу вообще.
    // Пока оставим базовую проверку на is_staff, т.к. детальные права роли могут быть не загружены в user store.
    // Либо, можно не проверять роль здесь, а положиться на ответ 403 от API при попытке загрузить/сохранить.
    if (!user || (!user.is_staff /* && !user.role?.can_manage_articles */)) { // Упрощенная проверка
      console.warn('Access to moderator/admin route denied.');
      next({ name: 'Home' }); // Или на страницу с ошибкой доступа
    } else {
      next();
    }
  }
  else {
    next();
  }
});

export default router
