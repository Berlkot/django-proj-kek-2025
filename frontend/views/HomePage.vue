<template>
  <div>
    <!-- 1. Поиск животных -->
    <section class="bg-amber-100 py-16 md:py-24 relative">
      <div class="absolute inset-0 z-0 opacity-40">
        <!-- Фоновое изображение будет здесь, если нужно. Пока просто цвет -->
        <!-- Для изображения: <img src="/path/to/hero-bg.jpg" alt="" class="w-full h-full object-cover"> -->
      </div>
      <div class="container mx-auto px-4 flex flex-col md:flex-row items-center relative z-10">
        <div class="md:w-1/2 text-center md:text-left mb-10 md:mb-0">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-800 mb-4">Поиск животных</h1>
          <p class="text-lg text-gray-700 mb-8">Найди или помоги другому найти своего любимца</p>
          <div class="flex max-w-md mx-auto md:mx-0">
            <input
              type="text"
              placeholder="Поиск животных..."
              class="flex-grow p-3 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500"
            />
            <button class="bg-green-500 text-white px-6 py-3 rounded-r-md hover:bg-green-600">
              Поиск
            </button>
          </div>
        </div>
        <div class="md:w-1/2 flex justify-center md:justify-end">
           <!-- Замените на ваш реальный путь к статическому изображению, если оно есть -->
           <img src="/images/hero-pets.png" alt="Собака и кошка" class="max-w-xs md:max-w-md rounded-lg shadow-lg">
         </div>
      </div>
    </section>

    <!-- 2. Последние объявления -->
    <section class="py-12 md:py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-800">Последние объявления</h2>
          <a href="/ads" class="text-green-600 hover:text-green-700 font-semibold">
            Посмотреть все >
          </a>
        </div>
        <div v-if="loading" class="text-center text-gray-500">Загрузка объявлений...</div>
        <div v-else-if="recentAds.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <AdCard
            v-for="ad in recentAds"
            :key="ad.id"
            :image-url="ad.first_photo_url || 'https://via.placeholder.com/300x200/cccccc/888888?text=No+Photo'"
            :title="ad.title"
            :description="ad.short_description"
            :location="ad.location"
            :time-ago="formatTimeAgo(ad.publication_date)"
          />
        </div>
        <div v-else-if="!loading && recentAds.length === 0" class="text-center text-gray-500">
            Нет доступных объявлений.
        </div>
        <div v-if="error" class="text-center text-red-500 mt-4">{{ error }}</div>
      </div>
    </section>

    <!-- 3. Статьи о питомцах -->
    <section class="py-12 md:py-16 bg-gray-100">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-3xl font-bold text-gray-800">Статьи о питомцах</h2>
          <a href="/articles" class="text-green-600 hover:text-green-700 font-semibold">
            Посмотреть все >
          </a>
        </div>
        <div v-if="loading" class="text-center text-gray-500">Загрузка статей...</div>
        <div v-else-if="mainArticle || sideArticles.length > 0" class="flex flex-col lg:flex-row gap-8">
          <!-- Большая статья слева -->
          <div v-if="mainArticle" class="lg:w-2/3">
            <div class="bg-white rounded-lg shadow-lg overflow-hidden">
              <img
                :src="mainArticle.main_image_url || 'https://via.placeholder.com/800x400/cccccc/888888?text=Article'"
                :alt="mainArticle.title"
                class="w-full h-64 object-cover"
              >
              <div class="p-6">
                <h3 class="text-2xl font-semibold text-gray-800 mb-2">{{ mainArticle.title }}</h3>
                <p class="text-gray-600 mb-4">{{ mainArticle.excerpt }}</p>
                <span class="text-sm text-gray-500">{{ formatTimeAgo(mainArticle.publication_date) }}</span>
              </div>
            </div>
          </div>
           <div v-else-if="!mainArticle && sideArticles.length === 0 && !loading" class="lg:w-2/3 text-center text-gray-500">
              Нет главной статьи для отображения.
          </div>

          <!-- Маленькие статьи справа -->
          <div v-if="sideArticles.length > 0" class="lg:w-1/3 space-y-6">
            <ArticleCard
              v-for="article in sideArticles"
              :key="article.id"
              :image-url="article.main_image_url || 'https://via.placeholder.com/400x250/cccccc/888888?text=Article'"
              :title="article.title"
              :description="article.excerpt"
              :time-ago="formatTimeAgo(article.publication_date)"
            />
          </div>
           <div v-else-if="sideArticles.length === 0 && !mainArticle && !loading" class="lg:w-1/3 text-center text-gray-500">
              Нет дополнительных статей.
          </div>
        </div>
         <div v-else-if="!loading && !mainArticle && sideArticles.length === 0" class="text-center text-gray-500">
            Нет доступных статей.
        </div>
        <div v-if="error" class="text-center text-red-500 mt-4">{{ error }}</div>
      </div>
    </section>

    <!-- ... (остальные секции: Приюты, Партнеры - пока без изменений) ... -->
    <!-- 4. Приюты -->
    <section class="py-12 md:py-16 bg-white">
      <div class="container mx-auto px-4">
        <div class="flex flex-col lg:flex-row items-center gap-8">
          <div class="lg:w-1/2 text-center lg:text-left">
            <h2 class="text-3xl font-bold text-gray-800 mb-4">Приюты</h2>
            <p class="text-gray-700 mb-6">
              Зачем куда-то далеко ходить или спрашивать у знакомых.
            </p>
            <p class="text-gray-700 mb-8">
              Легко найдите приют на интерактивной карте в шаге от вашего дома
            </p>
            <button class="bg-white text-green-600 border border-green-600 px-6 py-3 rounded-md hover:bg-green-50 font-semibold">
              О приютах
            </button>
          </div>
          <div class="lg:w-1/2">
            <img src="/images/map-placeholder.png" alt="Карта приютов" class="w-full rounded-lg shadow-md">
          </div>
        </div>
      </div>
    </section>

    <!-- 5. Партнеры (Спонсоры) -->
    <section class="py-12 bg-gray-100">
      <div class="container mx-auto px-4">
        <!-- Замените src на пути к вашим реальным логотипам в public/images/partners/ -->
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8 items-center justify-items-center">
          <img src="/images/partners/purina.png" alt="Purina" class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity">
          <img src="/images/partners/birulevo.png" alt="Приют Бирюлево" class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity">
          <img src="/images/partners/drug-sobaka.png" alt="Drug Sobaka" class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity">
          <img src="/images/partners/drug-dlya-druga.png" alt="Друг для друга" class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity">
          <img src="/images/partners/iskra.png" alt="Искра" class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity col-span-2 md:col-span-1 lg:col-auto justify-self-center">
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios'; // Убедитесь, что axios установлен: npm install axios
import AdCard from '../components/AdCard.vue';
import ArticleCard from '../components/ArticleCard.vue';

// Определяем интерфейсы для типов данных с API
interface Ad {
  id: number;
  title: string;
  short_description: string;
  publication_date: string; // ISO date string
  first_photo_url: string | null;
  location: string;
  species_name: string;
}

interface Article {
  id: number;
  title: string;
  excerpt: string;
  publication_date: string; // ISO date string
  author_name: string | null;
  main_image_url: string | null;
}

const recentAds = ref<Ad[]>([]);
const mainArticle = ref<Article | null>(null);
const sideArticles = ref<Article[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// URL вашего API (замените, если Django работает на другом порту/хосте)
const API_BASE_URL = 'http://localhost:8000/api'; // Или import.meta.env.VITE_API_URL, если настроено

const fetchData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await axios.get<{
      recent_ads: Ad[];
      main_article: Article | null;
      side_articles: Article[];
    }>(`${API_BASE_URL}/homepage/`);
    
    recentAds.value = response.data.recent_ads;
    mainArticle.value = response.data.main_article;
    sideArticles.value = response.data.side_articles;

  } catch (err) {
    console.error("Ошибка при загрузке данных для главной страницы:", err);
    if (axios.isAxiosError(err)) {
        error.value = `Не удалось загрузить данные: ${err.message}. Пожалуйста, проверьте ваше соединение и API.`;
    } else {
        error.value = "Произошла неизвестная ошибка при загрузке данных.";
    }
  } finally {
    loading.value = false;
  }
};

// Функция для форматирования даты (простой пример)
const formatTimeAgo = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.round((now.getTime() - date.getTime()) / 1000);
  const minutes = Math.round(seconds / 60);
  const hours = Math.round(minutes / 60);
  const days = Math.round(hours / 24);
  const months = Math.round(days / 30.44); // Среднее количество дней в месяце
  const years = Math.round(days / 365.25); // Учитываем високосные годы

  if (seconds < 60) return `${seconds} сек. назад`;
  if (minutes < 60) return `${minutes} мин. назад`;
  if (hours < 24) return `${hours} ч. назад`;
  if (days < 30) return `${days} дн. назад`;
  if (months < 12) return `${months} мес. назад`;
  return `${years} г. назад`;
};


onMounted(() => {
  fetchData();
});

</script>