<template>
  <div class="bg-gray-50 min-h-screen">
    <div v-if="loading" class="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <p class="text-xl text-gray-500">Загрузка объявления...</p>
    </div>
    <div v-else-if="error" class="container mx-auto px-4 py-10 text-center">
      <p class="text-xl text-red-500 bg-red-100 p-6 rounded-lg shadow">Ошибка: {{ error }}</p>
      <router-link :to="{ name: 'Advertisements' }" class="mt-6 inline-block bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600">
        Ко всем объявлениям
      </router-link>
    </div>
    <div v-else-if="ad" class="advertisement-detail-page">
      <!-- Хлебные крошки и название -->
      <div class="bg-white py-4 shadow-sm">
        <div class="container mx-auto px-4">
          <div class="text-sm text-gray-500 mb-3">
            <router-link :to="{ name: 'Advertisements' }" class="hover:text-green-600">Объявления</router-link>
            <span class="mx-1">»</span>
            <span class="truncate">{{ ad.title }}</span>
          </div>
          <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-1">{{ ad.title }}</h1>
          <div class="text-xs text-gray-500 flex items-center space-x-3">
            <span>Опубликовано: {{ formatTimeAgo(ad.publication_date) }}</span>
            <span v-if="ad.status" class="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs">{{ ad.status }}</span>
            <!-- TODO: просмотры, если будут -->
            <!-- <span><font-awesome-icon :icon="['fas', 'eye']" class="mr-1"/> 24 (24 сегодня)</span> -->
          </div>
        </div>
      </div>

      <div class="container mx-auto px-4 py-6 md:py-8">
        <div class="flex flex-col lg:flex-row gap-6 md:gap-8">
          <!-- Левая колонка: Галерея и Табы -->
          <div class="w-full lg:w-2/3">
            <ImageGallery :photos="ad.photos" />

            <!-- Табы -->
            <div class="mt-6 md:mt-8">
              <div class="border-b border-gray-200 mb-2">
                <nav class="-mb-px flex space-x-4 md:space-x-6" aria-label="Tabs">
                  <button
                    v-for="tab in tabs"
                    :key="tab.name"
                    @click="activeTab = tab.name"
                    :class="[
                      'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm md:text-base',
                      activeTab === tab.name
                        ? 'border-green-500 text-green-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                    ]"
                  >
                    {{ tab.label }}
                    <span v-if="tab.name === 'comments' && ad.responses.length > 0" class="ml-1 text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded-full">
                        {{ ad.responses.length }}
                    </span>
                  </button>
                </nav>
              </div>
              <div class="py-4">
                <!-- Содержимое табов -->
                <div v-show="activeTab === 'description'">
                  <h2 class="text-xl font-semibold text-gray-800 mb-3">Описание</h2>
                  <p class="text-gray-700 whitespace-pre-line leading-relaxed">{{ ad.description }}</p>

                  <div class="mt-6 pt-4 border-t border-gray-100">
                     <h3 class="text-lg font-semibold text-gray-800 mb-3">Информация о животном:</h3>
                     <ul class="space-y-1 text-gray-700 text-sm">
                        <li v-if="ad.animal.name"><span class="font-medium">Кличка:</span> {{ ad.animal.name }}</li>
                        <li><span class="font-medium">Вид:</span> {{ ad.animal.species }}</li>
                        <li v-if="ad.animal.breed"><span class="font-medium">Порода:</span> {{ ad.animal.breed }}</li>
                        <li><span class="font-medium">Возраст:</span> {{ ad.animal.age_years_months }}</li>
                        <li v-if="ad.animal.gender"><span class="font-medium">Пол:</span> {{ ad.animal.gender }}</li>
                        <li v-if="ad.animal.color"><span class="font-medium">Окрас:</span> {{ ad.animal.color }}</li>
                        <li v-if="ad.publication_date"><span class="font-medium">Дата {{ ad.status === 'Потеряно' ? 'потери' : (ad.status === 'Найдено' ? 'находки' : 'публикации') }}:</span> {{ formatDate(ad.publication_date) }}</li>
                     </ul>
                  </div>
                </div>
                <div v-show="activeTab === 'map'">
                  <h2 class="text-xl font-semibold text-gray-800 mb-3">Местоположение на карте</h2>
                  <div v-if="ad.latitude && ad.longitude" class="h-80 md:h-96 bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                    <!-- Здесь будет интеграция с картой (например, Яндекс.Карты или Leaflet) -->
                    Карта (широта: {{ ad.latitude.toFixed(4) }}, долгота: {{ ad.longitude.toFixed(4) }})
                    <p class="mt-2 text-xs">Интеграция карты в разработке.</p>
                  </div>
                  <p v-else class="text-gray-600">Местоположение не указано.</p>
                </div>
                <div v-show="activeTab === 'comments'">
                  <h2 class="text-xl font-semibold text-gray-800 mb-4">Комментарии ({{ ad.responses.length }})</h2>
                  <div v-if="ad.responses.length > 0" class="space-y-4">
                    <div v-for="response in ad.responses" :key="response.id" class="bg-white p-4 rounded-lg shadow-sm border">
                      <div class="flex items-start space-x-3">
                        <img :src="response.user.avatar_url || '/images/avatar-placeholder.png'" alt="avatar" class="w-10 h-10 rounded-full object-cover">
                        <div>
                          <p class="font-semibold text-gray-800">{{ response.user.display_name }}</p>
                          <p class="text-xs text-gray-500 mb-1">{{ formatTimeAgo(response.date_created) }}</p>
                          <p class="text-gray-700 text-sm whitespace-pre-line">{{ response.message }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <p v-else class="text-gray-600">Нет комментариев.</p>
                  <!-- Форма добавления комментария (позже) -->
                   <div class="mt-6 pt-4 border-t">
                        <h3 class="text-lg font-semibold mb-2">Оставить комментарий</h3>
                        <div v-if="isAuthenticated">
                            <textarea v-model="newCommentMessage" rows="3" placeholder="Ваш комментарий..." class="w-full p-2 border rounded-md focus:ring-green-500 focus:border-green-500"></textarea>
                            <button @click="submitComment" :disabled="commentSubmitting || !newCommentMessage.trim()" class="mt-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md disabled:opacity-50">
                                {{ commentSubmitting ? 'Отправка...' : 'Отправить' }}
                            </button>
                            <p v-if="commentError" class="text-red-500 text-sm mt-1">{{ commentError }}</p>
                        </div>
                        <div v-else>
                            <p class="text-sm text-gray-600">Чтобы оставить комментарий, пожалуйста, <router-link :to="{name: 'Login', query: { next: route.fullPath }}" class="text-green-600 hover:underline">войдите</router-link> или <router-link :to="{name: 'Register', query: { next: route.fullPath }}" class="text-green-600 hover:underline">зарегистрируйтесь</router-link>.</p>
                        </div>
                    </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Правая колонка: Информация об авторе -->
          <div class="w-full lg:w-1/3">
            <div class="bg-white p-5 rounded-lg shadow sticky top-20">
              <div class="flex items-center mb-4">
                <img :src="ad.user.avatar_url || '/static/images/no-image-data.png'" alt="avatar" class="w-16 h-16 rounded-full object-cover mr-4">
                <div>
                  <h3 class="text-xl font-semibold text-gray-800">{{ ad.user.display_name }}</h3>
                  <p v-if="ad.user.role" class="text-sm text-gray-500">{{ ad.user.role }}</p>
                </div>
              </div>
              <ul class="space-y-2 text-sm text-gray-700 mb-5">
                <li v-if="ad.user.region?.name" class="flex items-center">
                  <font-awesome-icon :icon="['fas', 'map-marker-alt']" class="w-4 h-4 mr-2 text-gray-400"/>
                  {{ ad.user.region.name }}
                </li>
                <li v-if="ad.user.phone_number" class="flex items-center">
                  <font-awesome-icon :icon="['fas', 'phone']" class="w-4 h-4 mr-2 text-gray-400"/>
                  <a :href="`tel:${ad.user.phone_number}`" class="hover:text-green-600">{{ ad.user.phone_number }}</a>
                </li>
                 <li v-if="ad.user.email" class="flex items-center">
                  <font-awesome-icon :icon="['fas', 'envelope']" class="w-4 h-4 mr-2 text-gray-400"/>
                  <a :href="`mailto:${ad.user.email}`" class="hover:text-green-600 truncate" :title="ad.user.email">{{ ad.user.email }}</a>
                </li>
              </ul>
              <button class="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-4 rounded-md transition duration-150 mb-2">
                Написать автору <!-- (может открывать модалку или вести на чат) -->
              </button>
              <router-link v-if="ad.user.id" :to="`/profile/${ad.user.id}`" class="block w-full text-center bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 px-4 rounded-md transition duration-150">
                Профиль автора
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import ImageGallery from '../components/ImageGallery.vue';
import { formatTimeAgo, formatDate } from '../utils/time';
import type { AdvertisementDetail, AdResponse } from '../types';
// import { useAuthStore } from '../stores/auth'; // Если есть Pinia store для аутентификации

const props = defineProps<{
  id: string | number;
}>();

const ad = ref<AdvertisementDetail | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const activeTab = ref('description');

const newCommentMessage = ref('');
const commentSubmitting = ref(false);
const commentError = ref<string | null>(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const route = useRoute();
const router = useRouter();
// const authStore = useAuthStore(); // Если используется
const isAuthenticated = ref(false); // Заглушка, замените на реальную проверку из authStore

const tabs = [
  { name: 'description', label: 'Описание' },
  { name: 'map', label: 'Карта' },
  { name: 'comments', label: 'Комментарии' },
];

const fetchAdDetail = async (adId: string | number) => {
  loading.value = true;
  error.value = null;
  ad.value = null;
  try {
    const response = await axios.get<AdvertisementDetail>(`${API_BASE_URL}/advertisements/${adId}/`);
    ad.value = response.data;
    // Проверка аутентификации для возможности комментирования
    // isAuthenticated.value = authStore.isAuthenticated; // Пример
  } catch (err) {
    console.error(`Ошибка загрузки объявления ${adId}:`, err);
    error.value = axios.isAxiosError(err) ? (err.response?.status === 404 ? "Объявление не найдено." : `Ошибка: ${err.message}`) : "Неизвестная ошибка";
  } finally {
    loading.value = false;
  }
};

const submitComment = async () => {
    if (!newCommentMessage.value.trim() || !ad.value) return;
    commentSubmitting.value = true;
    commentError.value = null;
    try {
        // Предполагается, что у вас настроен Axios для отправки токена авторизации
        const response = await axios.post<AdResponse>(
            `${API_BASE_URL}/advertisements/${ad.value.id}/responses/`,
            { message: newCommentMessage.value }
            // Headers с токеном должны быть добавлены глобально или через interceptors
        );
        if (ad.value.responses) {
            ad.value.responses.unshift(response.data); // Добавляем новый коммент в начало
        } else {
            ad.value.responses = [response.data];
        }
        newCommentMessage.value = '';
    } catch (err) {
        console.error("Ошибка отправки комментария:", err);
        commentError.value = axios.isAxiosError(err) ? `Ошибка: ${err.response?.data?.detail || err.message}` : "Не удалось отправить комментарий.";
    } finally {
        commentSubmitting.value = false;
    }
};

onMounted(() => {
  fetchAdDetail(props.id);
  // Заглушка для isAuthenticated - получите реальное значение из вашего хранилища состояния (Pinia/Vuex)
  // Например, если вы используете localStorage для токена:
  isAuthenticated.value = !!localStorage.getItem('authToken'); 
});

watch(() => props.id, (newId) => {
  if (newId) {
    fetchAdDetail(newId);
    activeTab.value = 'description'; // Сброс на первую вкладку при смене объявления
  }
});
</script>

<style scoped>
/* Стили для активной вкладки и других элементов, если нужно */
.whitespace-pre-line {
  white-space: pre-line;
}
</style>