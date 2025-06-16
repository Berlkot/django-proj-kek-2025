<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="container mx-auto px-4 py-3 flex justify-between items-center">
      <router-link to="/" class="flex items-center">
        <img src="/logo.svg" alt="СпасиЗверя" class="h-10 mr-2" />
      </router-link>

      <nav class="hidden md:flex items-center space-x-4 lg:space-x-6 text-gray-700">
        <router-link
          :to="{ name: 'Advertisements' }"
          class="hover:text-green-600"
          active-class="text-green-600 font-semibold"
          >Объявления</router-link
        >
        <router-link
          :to="{ name: 'Rules' }"
          class="hover:text-green-600"
          active-class="text-green-600 font-semibold"
          >Правила</router-link
        >
        <router-link
          :to="{ name: 'Contacts' }"
          class="hover:text-green-600"
          active-class="text-green-600 font-semibold"
          >Контакты</router-link
        >
        <router-link
          :to="{ name: 'Articles' }"
          class="hover:text-green-600"
          active-class="text-green-600 font-semibold"
          >Статьи</router-link
        >
      </nav>

      <div class="hidden md:flex items-center space-x-3">
        <template v-if="!authStore.isAuthenticated">
          <button
            @click="navigateTo({ name: 'Login' })"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
          >
            Войти
          </button>
          <button
            @click="navigateTo({ name: 'Register' })"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Регистрация
          </button>
        </template>
        <template v-else>
          <Menu as="div" class="relative">
            <MenuButton
              class="flex items-center space-x-2 px-3 py-1.5 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
            >
              <img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                alt="Аватар"
                class="w-7 h-7 rounded-full object-cover"
              />
              <span
                v-else
                class="w-7 h-7 rounded-full bg-gray-300 flex items-center justify-center text-sm text-gray-600"
              >
                {{
                  authStore.user?.display_name?.charAt(0) ||
                  authStore.user?.username?.charAt(0) ||
                  '?'
                }}
              </span>
              <span class="hidden sm:inline">{{
                authStore.user?.display_name || authStore.user?.username
              }}</span>
              <font-awesome-icon :icon="['fas', 'chevron-down']" class="w-3 h-3 text-gray-500" />
            </MenuButton>
            <transition
              enter-active-class="transition ease-out duration-100"
              enter-from-class="transform opacity-0 scale-95"
              enter-to-class="transform opacity-100 scale-100"
              leave-active-class="transition ease-in duration-75"
              leave-from-class="transform opacity-100 scale-100"
              leave-to-class="transform opacity-0 scale-95"
            >
              <MenuItems
                class="absolute right-0 mt-2 w-48 origin-top-right bg-white divide-y divide-gray-100 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
              >
                <div class="px-1 py-1">
                  <MenuItem v-if="authStore.user?.is_staff" v-slot="{ active }">
                    <router-link
                      :to="{ name: 'AdminUsers' }"
                      :class="[
                        'group flex w-full items-center rounded-md px-2 py-2 text-sm',
                        active ? 'bg-indigo-500 text-white' : 'text-gray-900',
                      ]"
                    >
                      Админ-панель
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <router-link
                      :to="{ name: 'Profile', params: { id: authStore.user?.id } }"
                      :class="[
                        'group flex w-full items-center rounded-md px-2 py-2 text-sm',
                        active ? 'bg-green-500 text-white' : 'text-gray-900',
                      ]"
                    >
                      Мой профиль
                    </router-link>
                  </MenuItem>
                  <MenuItem v-slot="{ active }">
                    <button
                      @click="handleLogout"
                      :class="[
                        'group flex w-full items-center rounded-md px-2 py-2 text-sm',
                        active ? 'bg-red-500 text-white' : 'text-gray-900',
                      ]"
                    >
                      Выйти
                    </button>
                  </MenuItem>
                </div>
              </MenuItems>
            </transition>
          </Menu>
        </template>
        <button
          @click="handlePostAdClick"
          class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
        >
          Разместить
        </button>
      </div>

      <div class="md:hidden">
        <button @click="toggleMobileMenu" class="text-gray-700 focus:outline-none">
          <font-awesome-icon :icon="['fas', 'bars']" class="w-6 h-6" />
        </button>
      </div>
    </div>

    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 -translate-y-10"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 -translate-y-10"
    >
      <div
        v-if="isMobileMenuOpen"
        class="md:hidden absolute top-full left-0 right-0 bg-white shadow-lg z-40"
      >
        <nav class="flex flex-col px-4 pt-2 pb-4 space-y-1 border-t border-gray-200">
          <router-link
            @click="closeMobileMenu"
            :to="{ name: 'Advertisements' }"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600"
            active-class="bg-gray-100 text-green-600"
            >Объявления</router-link
          >
          <router-link
            @click="closeMobileMenu"
            to="/rules"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600"
            >Правила</router-link
          >
          <router-link
            @click="closeMobileMenu"
            to="/contacts"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600"
            >Контакты</router-link
          >
          <router-link
            @click="closeMobileMenu"
            :to="{ name: 'Articles' }"
            class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600"
            active-class="bg-gray-100 text-green-600"
            >Статьи</router-link
          >
          <hr class="my-2" />
          <template v-if="!authStore.isAuthenticated">
            <button
              @click="handleMobileAuthClick({ name: 'Login' })"
              class="w-full text-left block px-3 py-2 border border-gray-300 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100"
            >
              Войти
            </button>
            <button
              @click="handleMobileAuthClick({ name: 'Register' })"
              class="w-full text-left block mt-2 px-3 py-2 bg-green-500 text-white rounded-md text-base font-medium hover:bg-green-600"
            >
              Регистрация
            </button>
          </template>
          <template v-else>
            <router-link
              @click="closeMobileMenu"
              :to="{ name: 'Profile', params: { id: authStore.user?.id } }"
              class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600"
            >
              <div class="flex items-center">
                <img
                  v-if="authStore.user?.avatar_url"
                  :src="authStore.user.avatar_url"
                  alt="Аватар"
                  class="w-7 h-7 rounded-full object-cover mr-2"
                />
                <span
                  v-else
                  class="w-7 h-7 rounded-full bg-gray-300 flex items-center justify-center text-sm text-gray-600 mr-2"
                >
                  {{
                    authStore.user?.display_name?.charAt(0) ||
                    authStore.user?.username?.charAt(0) ||
                    '?'
                  }}
                </span>
                Мой профиль
              </div>
            </router-link>
            <button
              @click="handleMobileLogout"
              class="w-full text-left block mt-2 px-3 py-2 border border-red-500 text-red-500 rounded-md text-base font-medium hover:bg-red-50"
            >
              Выйти
            </button>
          </template>
        </nav>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, type RouteLocationNamedRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue'

const authStore = useAuthStore()
const router = useRouter()

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => (isMobileMenuOpen.value = !isMobileMenuOpen.value)
const closeMobileMenu = () => (isMobileMenuOpen.value = false)

const navigateTo = (location: RouteLocationNamedRaw) => {
  router.push(location)
}

const handleMobileAuthClick = (location: RouteLocationNamedRaw) => {
  closeMobileMenu()
  navigateTo(location)
}

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'Home' })
}
const handleMobileLogout = () => {
  closeMobileMenu()
  handleLogout()
}

const handlePostAdClick = () => {
  if (
    authStore.isAuthenticated &&
    (authStore.user?.is_staff || authStore.user?.role_permissions?.can_create_advertisement)
  ) {
    router.push({ name: 'AdvertisementCreate' })
  } else if (
    authStore.isAuthenticated &&
    !(authStore.user?.is_staff || authStore.user?.role_permissions?.can_create_advertisement)
  ) {
    alert('У вас недостаточно прав для создания объявления.')
  } else {
    const createAdRoute = router.resolve({ name: 'AdvertisementCreate' })
    router.push({ name: 'Login', query: { next: createAdRoute.fullPath } })
  }
}
</script>
