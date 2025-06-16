import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ArticlesPage from '../views/ArticlesPage.vue'
import AdvertisementsPage from '../views/AdvertisementsPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import ArticleEditPage from '../views/ArticleEditPage.vue'
import AdvertisementEditPage from '../views/AdvertisementEditPage.vue'
import { useAuthStore } from '../stores/auth'

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
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/articles/create',
    name: 'ArticleCreate',
    component: ArticleEditPage,
    meta: { requiresAuth: true, requiresAdmin: true },
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
    props: true,
  },
  {
    path: '/advertisements/edit/:id(\\d+)',
    name: 'AdvertisementEdit',
    component: AdvertisementEditPage,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/advertisements/create',
    name: 'AdvertisementCreate',
    component: AdvertisementEditPage,
    meta: { requiresAuth: true },
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
  {
    path: '/profile/:id(\\d+)',
    name: 'Profile',
    component: () => import('../views/ProfilePage.vue'),
    props: true,
  },
  {
    path: '/admin-panel/users',
    name: 'AdminUsers',
    component: () => import('../views/AdminUsersPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
     path: '/social/auth/callback/',
     name: 'SocialAuthCallback',
     component: () => import('../views/SocialAuthCallback.vue'),
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

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const user = authStore.user
  const isAdminRoute = to.matched.some((record) => record.meta.requiresAdmin)
  if (isAdminRoute && (!user || !user.is_staff)) {
    console.warn('Access to admin route denied.')
    next({ name: 'Home' })
  } else if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { next: to.fullPath } })
  } else if (to.meta.guestOnly && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
