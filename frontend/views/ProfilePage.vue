<template>
  <div class="bg-gray-100 min-h-screen">
    <div v-if="loading" class="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <p class="text-xl text-gray-500">Загрузка профиля...</p>
    </div>
    <div v-else-if="error" class="container mx-auto px-4 py-10 text-center">
      <p class="text-xl text-red-500 bg-red-100 p-6 rounded-lg shadow">Ошибка: {{ error }}</p>
      <router-link
        :to="{ name: 'Home' }"
        class="mt-6 inline-block bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600"
      >
        На главную
      </router-link>
    </div>

    <div v-else-if="profileData" class="profile-page">
      <div class="container mx-auto px-4 py-8 md:py-12">
        <div class="bg-white p-6 md:p-8 rounded-lg shadow-md mb-8">
          <!-- Profile Header -->
          <div
            class="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left"
          >
            <div class="relative mb-4 sm:mb-0 sm:mr-6 flex-shrink-0">
              <img
                :src="
                  imagePreviewUrl ||
                  profileData.user.avatar_url ||
                  '/static/images/no-image-data.png'
                "
                alt="Аватар пользователя"
                class="w-28 h-28 md:w-32 md:h-32 rounded-full object-cover border-4 border-white shadow-lg"
              />
              <label
                v-if="isEditMode"
                for="avatar-upload"
                class="absolute bottom-0 right-0 bg-gray-700 text-white rounded-full p-2 cursor-pointer hover:bg-gray-800 transition"
              >
                <font-awesome-icon icon="pencil-alt" class="w-4 h-4" />
                <input
                  type="file"
                  id="avatar-upload"
                  class="hidden"
                  @change="handleAvatarChange"
                  accept="image/*"
                />
              </label>
            </div>
            <div class="flex-grow">
              <h1 v-if="!isEditMode" class="text-3xl font-bold text-gray-800">
                {{ profileData.user.display_name }}
              </h1>
              <div
                v-if="!isEditMode"
                class="flex items-center justify-center sm:justify-start space-x-4 mt-2 text-gray-500"
              >
                <span
                  v-if="profileData.user.role_name"
                  class="text-sm font-semibold text-green-600"
                  >{{ profileData.user.role_name }}</span
                >
                <span>Зарегистрирован: {{ formatDate(profileData.user.date_joined) }}</span>
              </div>

              <!-- Edit Mode: Name Inputs -->
              <div v-if="isEditMode" class="space-y-3">
                <input
                  type="text"
                  v-model="formData.display_name"
                  placeholder="Отображаемое имя"
                  class="text-2xl font-bold text-gray-800 w-full p-2 border rounded-md"
                />
                <p v-if="formErrors.display_name" class="text-red-500 text-xs mt-1">
                  {{ formErrors.display_name.join(', ') }}
                </p>

                <div class="grid grid-cols-2 gap-2">
                  <div>
                    <input
                      type="text"
                      v-model="formData.first_name"
                      placeholder="Имя"
                      class="w-full p-2 border rounded-md"
                    />
                    <p v-if="formErrors.first_name" class="text-red-500 text-xs mt-1">
                      {{ formErrors.first_name.join(', ') }}
                    </p>
                  </div>
                  <div>
                    <input
                      type="text"
                      v-model="formData.last_name"
                      placeholder="Фамилия"
                      class="w-full p-2 border rounded-md"
                    />
                    <p v-if="formErrors.last_name" class="text-red-500 text-xs mt-1">
                      {{ formErrors.last_name.join(', ') }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="canEdit" class="mt-4 sm:mt-0 ml-auto flex-shrink-0 space-x-2">
              <template v-if="!isEditMode">
                <button
                  @click="enterEditMode"
                  class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm"
                >
                  Редактировать
                </button>
              </template>
              <template v-else>
                <button
                  @click="handleProfileUpdate"
                  :disabled="submitting"
                  class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 text-sm disabled:opacity-50"
                >
                  Сохранить
                </button>
                <button
                  @click="cancelEditMode"
                  class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm"
                >
                  Отмена
                </button>
              </template>
            </div>
          </div>

          <!-- Contact and Admin section -->
          <div class="mt-6 border-t pt-6">
            <div v-if="!isEditMode" class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="font-semibold text-gray-600 mb-2">Контактная информация</h3>
                <p>Email: {{ profileData.user.email }}</p>
                <p>Телефон: {{ profileData.user.phone_number || 'Не указан' }}</p>
                <p>Регион: {{ profileData.user.region_name || 'Не указан' }}</p>
              </div>
              <div v-if="isAdmin && profileData.user.id !== authStore.user?.id">
                <h3 class="font-semibold text-gray-600 mb-2">Администрирование</h3>
                <div class="flex items-center space-x-2">
                  <button
                    @click="handleDeleteUser"
                    :disabled="deleting"
                    class="px-3 py-1.5 bg-red-600 text-white rounded-md text-xs hover:bg-red-700 disabled:opacity-50"
                  >
                    Удалить пользователя
                  </button>
                </div>
              </div>
            </div>

            <div v-if="isEditMode" class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="font-semibold text-gray-600 mb-2">Контактная информация</h3>
                <div class="space-y-2">
                  <div>
                    <input
                      type="email"
                      v-model="formData.email"
                      placeholder="Email"
                      class="w-full p-2 border rounded-md"
                    />
                    <p v-if="formErrors.email" class="text-red-500 text-xs mt-1">
                      {{ formErrors.email.join(', ') }}
                    </p>
                  </div>
                  <div>
                    <input
                      type="tel"
                      v-model="formData.phone_number"
                      placeholder="Номер телефона"
                      class="w-full p-2 border rounded-md"
                    />
                    <p v-if="formErrors.phone_number" class="text-red-500 text-xs mt-1">
                      {{ formErrors.phone_number.join(', ') }}
                    </p>
                  </div>
                  <div>
                    <select v-model="formData.region" class="w-full p-2 border rounded-md bg-white">
                      <option :value="null">Регион не выбран</option>
                      <option v-for="region in regions" :key="region.id" :value="region.id">
                        {{ region.name }}
                      </option>
                    </select>
                    <p v-if="formErrors.region" class="text-red-500 text-xs mt-1">
                      {{ formErrors.region.join(', ') }}
                    </p>
                  </div>
                </div>
              </div>
              <div v-if="isAdmin">
                <h3 class="font-semibold text-gray-600 mb-2">Администрирование</h3>
                <div class="space-y-2">
                  <select v-model="formData.role" class="w-full p-2 border rounded-md bg-white">
                    <option :value="null">-- Без роли (Блокировка) --</option>
                    <option v-for="role in roles" :key="role.id" :value="role.id">
                      {{ role.name }}
                    </option>
                  </select>
                  <p v-if="formErrors.role" class="text-red-500 text-xs mt-1">
                    {{ formErrors.role.join(', ') }}
                  </p>

                  <label class="flex items-center space-x-2">
                    <input type="checkbox" v-model="formData.is_staff" />
                    <span>Статус администратора (is_staff)</span>
                  </label>
                  <p v-if="formErrors.is_staff" class="text-red-500 text-xs mt-1">
                    {{ formErrors.is_staff.join(', ') }}
                  </p>
                </div>
              </div>
            </div>
            <!-- ИЗМЕНЯЕМ ОБЩУЮ ОШИБКУ -->
            <p v-if="submitError" class="text-red-500 text-sm mt-4 bg-red-50 p-3 rounded-md">
              {{ submitError }}
            </p>
            <p
              v-if="formErrors.non_field_errors"
              class="text-red-500 text-sm mt-4 bg-red-50 p-3 rounded-md"
            >
              {{ formErrors.non_field_errors.join(', ') }}
            </p>
          </div>
        </div>

        <!-- User's Advertisements -->
        <div>
          <h2 class="text-2xl font-bold text-gray-800 mb-6">
            Объявления пользователя ({{ profileData.advertisements.length }})
          </h2>
          <div
            v-if="profileData.advertisements.length > 0"
            class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6"
          >
            <AdCard
              v-for="ad in profileData.advertisements"
              :key="ad.id"
              :id="ad.id"
              :image-url="ad.first_photo_url || '/static/images/no-image-data.png'"
              :title="ad.title"
              :description="ad.short_description"
              :location="ad.location"
              :time-ago="formatTimeAgo(ad.publication_date)"
              :ad-type="ad.status"
              :species-name="ad.animal.species"
            />
          </div>
          <div v-else class="text-center py-10 bg-white rounded-lg shadow-md">
            <p class="text-gray-500">У этого пользователя еще нет объявлений.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { formatDate, formatTimeAgo } from '../utils/time'
import AdCard from '../components/AdCard.vue'
import type { ProfileData, ProfileFormData, Role, Region } from '../types'

const props = defineProps<{ id: string | number }>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const profileData = ref<ProfileData | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const submitting = ref(false)
const deleting = ref(false)
const submitError = ref<string | null>(null)

const isEditMode = ref(false)
const imagePreviewUrl = ref<string | null>(null)
const roles = ref<Role[]>([])
const regions = ref<Region[]>([])
const formErrors = ref<Record<string, string[]>>({})

const defaultFormData = (): ProfileFormData => ({
  display_name: '',
  first_name: '',
  last_name: '',
  phone_number: null,
  region: null,
  avatar: null,
  role: undefined,
  is_staff: false,
  email: '',
})
const formData = reactive<ProfileFormData>(defaultFormData())

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// --- Computed Properties ---
const isOwner = computed(() => authStore.user?.id === profileData.value?.user.id)
const isAdmin = computed(() => authStore.user?.is_staff || false)
const canEdit = computed(() => isOwner.value || isAdmin.value)

// --- Data Fetching ---
const fetchProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get<ProfileData>(`${API_BASE_URL}/profiles/${props.id}/`)
    profileData.value = response.data
  } catch (err) {
    console.error('Profile fetch error:', err)
    error.value = axios.isAxiosError(err)
      ? `Ошибка: ${err.response?.data?.detail || err.message}`
      : 'Неизвестная ошибка'
  } finally {
    loading.value = false
  }
}

const fetchAdminData = async () => {
  if (!isAdmin.value) return
  try {
    const [rolesRes, regionsRes] = await Promise.all([
      axios.get<Role[]>(`${API_BASE_URL}/roles/`),
      axios.get<any>(`${API_BASE_URL}/filter-options/`), // Получаем регионы отсюда
    ])
    roles.value = rolesRes.data
    regions.value = regionsRes.data.regions
  } catch (err) {
    console.warn('Could not fetch admin data (roles/regions):', err)
  }
}

onMounted(() => {
  fetchProfile()
  fetchAdminData()
})

// --- Edit Mode Logic ---
const enterEditMode = () => {
  if (!profileData.value) return
  const user = profileData.value.user
  formData.display_name = user.display_name || ''
  formData.first_name = user.first_name || ''
  formData.last_name = user.last_name || ''
  formData.phone_number = user.phone_number || null
  formData.email = user.email || ''

  const currentRegion = regions.value.find((r) => r.name === user.region_name)
  formData.region = currentRegion ? currentRegion.id : null

  if (isAdmin.value) {
    const currentRole = roles.value.find((r) => r.name === user.role_name)
    formData.role = currentRole ? currentRole.id : null
    formData.is_staff = user.is_staff || false
  }
  isEditMode.value = true
}

const cancelEditMode = () => {
  isEditMode.value = false
  imagePreviewUrl.value = null
  // Reset form data if needed
  Object.assign(formData, defaultFormData())
}

const handleAvatarChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    formData.avatar = file
    imagePreviewUrl.value = URL.createObjectURL(file)
  }
}

// --- API Actions ---
const handleProfileUpdate = async () => {
  if (!canEdit.value) return
  submitting.value = true
  submitError.value = null
  formErrors.value = {} // Сбрасываем ошибки полей перед каждым запросом

  const data = new FormData()
  // ... (логика сборки FormData остается прежней)
  data.append('display_name', formData.display_name)
  data.append('first_name', formData.first_name)
  data.append('last_name', formData.last_name)
  data.append('email', formData.email)

  if (formData.phone_number) data.append('phone_number', formData.phone_number)
  else data.append('phone_number', '')

  if (formData.region) data.append('region', String(formData.region))
  if (formData.avatar) data.append('avatar', formData.avatar)

  if (isAdmin.value) {
    if (formData.role !== undefined) {
      data.append('role', formData.role === null ? '' : String(formData.role))
    }
    if (formData.is_staff !== undefined) {
      data.append('is_staff', String(formData.is_staff))
    }
  }

  try {
    const response = await axios.patch<ProfileData['user']>(
      `${API_BASE_URL}/profiles/${props.id}/`,
      data,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      },
    )

    if (profileData.value) {
      profileData.value.user = response.data
    }

    if (isOwner.value) {
      await authStore.fetchUser()
    }
    cancelEditMode()
  } catch (err) {
    console.error('Update error:', err)

    if (axios.isAxiosError(err) && err.response?.data) {
      const errors = err.response.data
      // Проверяем, является ли объект ошибок объектом (для ошибок по полям)
      if (typeof errors === 'object' && !Array.isArray(errors)) {
        formErrors.value = errors
      } else {
        // Иначе это общая ошибка
        submitError.value = Array.isArray(errors) ? errors.join(', ') : String(errors)
      }
    } else {
      submitError.value = 'Произошла неизвестная сетевая ошибка.'
    }
  } finally {
    submitting.value = false
  }
}

const handleDeleteUser = async () => {
  if (
    !isAdmin.value ||
    !confirm(
      `Вы уверены, что хотите удалить пользователя ${profileData.value?.user.username}? Это действие необратимо.`,
    )
  )
    return
  deleting.value = true
  submitError.value = null
  try {
    await axios.delete(`${API_BASE_URL}/profiles/${props.id}/`)
    alert('Пользователь удален.')
    router.push({ name: 'Home' })
  } catch (err) {
    console.error('Delete user error:', err)
    submitError.value = 'Не удалось удалить пользователя.'
  } finally {
    deleting.value = false
  }
}
</script>
