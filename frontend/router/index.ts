import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import AdvertisementsPage from '../views/AdvertisementsPage.vue'
import LoginPage from '../views/LoginPage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import ArticleEditPage from '../views/ArticleEditPage.vue';
import AdvertisementEditPage from '../views/AdvertisementEditPage.vue';
import { useAuthStore } from '../stores/auth';

// Определяем тип для маршрутов для лучшей типизации
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/articles',
    name: 'Articles',
    component: ArticlesPage,
  },
  {
    path: '/article/:id(\\d+)',
    name: 'ArticleDetail',
    component: () => import('../views/ArticleDetailPage.vue'),
    props: true,
  },
  {
    path: '/articles/edit/:id(\\d+)',
    name: 'ArticleEdit',
    component: ArticleEditPage,
    props: true,
    meta: { requiresAuth: true, requiresModeratorOrAdmin: true }
  },
  {
    path: '/articles/create',
    name: 'ArticleCreate',
    component: ArticleEditPage,
    meta: { requiresAuth: true, requiresModeratorOrAdmin: true }
  },
  {
    path: '/advertisements',
    name: 'Advertisements',
    component: AdvertisementsPage,
  },

  {
     path: '/advertisement/:id(\\d+)',
     name: 'AdvertisementDetail',
     component: () => import('../views/AdvertisementDetailPage.vue'),
     props: true
   },
   {
     path: '/advertisements/edit/:id(\\d+)',
     name: 'AdvertisementEdit',
     component: AdvertisementEditPage,
     props: true,
     meta: { requiresAuth: true /* , requiresAdPermission: true */ }
   },
   {
     path: '/advertisements/create',
     name: 'AdvertisementCreate',
     component: AdvertisementEditPage,
     meta: { requiresAuth: true /* , requiresAdPermission: true */ }
   },
  {
    path: '/rules',
    name: 'Rules',
    component: HomePage,
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: HomePage,
  },
  {
    path: '/post-ad',
    name: 'PostAd',
    component: HomePage,
  },
  { path: '/login', name: 'Login', component: LoginPage, meta: { guestOnly: true } },
  { path: '/register', name: 'Register', component: RegisterPage, meta: { guestOnly: true } },
  {
    path: '/privacy',
    name: 'Privacy',
    component: HomePage,
  },
  {
    path: '/sitemap',
    name: 'Sitemap',
    component: HomePage,
  },
  {
    path: '/shelters',
    name: 'Shelters',
    component: HomePage,
  },


]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {

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




    const user = authStore.user;





    if (!user || (!user.is_staff /* && !user.role?.can_manage_articles */)) {
      console.warn('Access to moderator/admin route denied.');
      next({ name: 'Home' });
    } else {
      next();
    }
  }
  else {
    next();
  }
});

export default router
