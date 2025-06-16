<template>
  <div class="bg-gray-100 min-h-screen">
    <div class="container mx-auto px-4 py-8 md:py-12">
      <div class="flex flex-col sm:flex-row justify-between sm:items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-800 mb-2 sm:mb-0">Управление пользователями</h1>
        <div class="text-sm text-gray-600">Найдено: {{ totalUsersCount }}</div>
      </div>

      <!-- Search and Filter Bar -->
      <div class="mb-6 bg-white p-4 rounded-lg shadow-sm">
        <div class="flex items-center">
          <input
            type="text"
            v-model="searchQuery"
            @keyup.enter="applySearch"
            placeholder="Поиск по email, имени, логину..."
            class="w-full p-2 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500"
          />
          <button
            @click="applySearch"
            class="bg-green-500 text-white px-5 py-2 rounded-r-md hover:bg-green-600"
            aria-label="Поиск"
          >
            <font-awesome-icon :icon="['fas', 'search']" />
          </button>
        </div>
      </div>

      <!-- Users Table -->
      <div class="bg-white rounded-lg shadow-md overflow-x-auto">
        <div v-if="loading" class="p-8 text-center text-gray-500">Загрузка пользователей...</div>
        <div v-else-if="error" class="p-8 text-center text-red-500">{{ error }}</div>
        <table v-else-if="users.length > 0" class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                ID
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Пользователь
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Роль
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Статус
              </th>
              <th
                scope="col"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Дата регистрации
              </th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">Действия</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ user.display_name || user.username }}
                </div>
                <div class="text-sm text-gray-500">{{ user.email }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ user.role_name || 'Нет роли' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  "
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                >
                  {{ user.is_active ? 'Активен' : 'Неактивен' }}
                </span>
                <span
                  v-if="user.is_staff"
                  class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-indigo-100 text-indigo-800"
                >
                  Админ
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(user.date_joined) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <router-link
                  :to="{ name: 'Profile', params: { id: user.id } }"
                  class="text-green-600 hover:text-green-900"
                >
                  Редактировать
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="p-8 text-center text-gray-500">Пользователи не найдены.</div>
      </div>

      <!-- Pagination -->
      <div v-if="!loading && totalPages > 1" class="mt-6 flex justify-center">
        <nav
          class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px"
          aria-label="Pagination"
        >
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
          >
            Назад
          </button>
          <button
            v-for="page in paginationNumbers"
            :key="page"
            @click="changePage(page)"
            :disabled="page === '...'"
            :class="[
              'relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium',
              page === currentPage
                ? 'z-10 bg-green-50 border-green-500 text-green-600'
                : 'bg-white text-gray-700 hover:bg-gray-50',
            ]"
          >
            {{ page }}
          </button>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
          >
            Вперед
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { formatDate } from '../utils/time'
import type { AdminUser, PaginatedAdminUsersResponse } from '../types'

const users = ref<AdminUser[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const totalUsersCount = ref(0)
const totalPages = ref(1)
const currentPage = ref(1)
const searchQuery = ref('')
const currentSearchTerm = ref('')

const route = useRoute()
const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
    }
    if (currentSearchTerm.value) {
      params.search = currentSearchTerm.value
    }
    const response = await axios.get<PaginatedAdminUsersResponse>(`${API_BASE_URL}/admin/users/`, {
      params,
    })
    users.value = response.data.results
    totalUsersCount.value = response.data.count
    totalPages.value = Math.ceil(response.data.count / 15)
  } catch (err) {
    console.error('Fetch users error:', err)
    error.value = 'Не удалось загрузить список пользователей.'
  } finally {
    loading.value = false
  }
}

const updateRouteQuery = () => {
  const query: Record<string, any> = {}
  if (currentPage.value > 1) query.page = currentPage.value
  if (currentSearchTerm.value) query.search = currentSearchTerm.value
  router.push({ query })
}

const applySearch = () => {
  currentPage.value = 1
  currentSearchTerm.value = searchQuery.value
  updateRouteQuery()
}

const changePage = (page: number | string) => {
  if (typeof page === 'string' || page < 1 || page > totalPages.value) return
  currentPage.value = page
  updateRouteQuery()
}

watch(
  () => route.query,
  (newQuery) => {
    currentPage.value = newQuery.page ? parseInt(newQuery.page as string) : 1
    currentSearchTerm.value = (newQuery.search as string) || ''
    searchQuery.value = currentSearchTerm.value
    fetchUsers()
  },
  { immediate: true },
)

const paginationNumbers = computed(() => {
  const delta = 1
  const range: (number | string)[] = []
  const rangeWithDots: (number | string)[] = []
  let l: number | undefined

  range.push(1)
  for (let i = currentPage.value - delta; i <= currentPage.value + delta; i++) {
    if (i >= 2 && i < totalPages.value) {
      range.push(i)
    }
  }
  if (totalPages.value > 1) {
    range.push(totalPages.value)
  }

  range.forEach((i) => {
    if (l !== undefined) {
      if (i > l + 1) {
        rangeWithDots.push('...')
      }
    }
    rangeWithDots.push(i)
    l = Number(i)
  })

  return rangeWithDots
})
</script>
