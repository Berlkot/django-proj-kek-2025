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
          <!-- Изображение собаки и кошки -->
          <img src="https://via.placeholder.com/400x300/cccccc/888888?text=Dog+and+Cat" alt="Собака и кошка" class="max-w-xs md:max-w-md rounded-lg shadow-lg">
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
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- Пример карточки объявления (повторить 4 раза) -->
          <AdCard
            v-for="ad in recentAds"
            :key="ad.id"
            :image-url="ad.imageUrl"
            :title="ad.title"
            :description="ad.description"
            :location="ad.location"
            :time-ago="ad.timeAgo"
          />
        </div>
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
        <div class="flex flex-col lg:flex-row gap-8">
          <!-- Большая статья слева -->
          <div class="lg:w-2/3">
            <div class="bg-white rounded-lg shadow-lg overflow-hidden">
              <img src="https://via.placeholder.com/800x400/cccccc/888888?text=Main+Article+Cat" alt="Как закапать глаза кошке" class="w-full h-64 object-cover">
              <div class="p-6">
                <h3 class="text-2xl font-semibold text-gray-800 mb-2">Как закапать глаза кошке</h3>
                <p class="text-gray-600 mb-4">Как закапать глаза кошке: порядок лечения, подготовка, пошаговое описание процедуры и побочные эффекты.</p>
                <span class="text-sm text-gray-500">11 месяцев назад</span>
              </div>
            </div>
          </div>
          <!-- Маленькие статьи справа -->
          <div class="lg:w-1/3 space-y-6">
            <ArticleCard
              v-for="article in sideArticles"
              :key="article.id"
              :image-url="article.imageUrl"
              :title="article.title"
              :description="article.description"
              :time-ago="article.timeAgo"
            />
          </div>
        </div>
      </div>
    </section>

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
            <!-- Карта (пока плейсхолдер) -->
            <img src="https://via.placeholder.com/600x400/eeeeee/999999?text=Interactive+Map+Placeholder" alt="Карта приютов" class="w-full rounded-lg shadow-md">
          </div>
        </div>
      </div>
    </section>

    <!-- 5. Партнеры (Спонсоры) -->
    <section class="py-12 bg-gray-100">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8 items-center justify-items-center">
          <img src="https://via.placeholder.com/150x60/cccccc/888888?text=Purina" alt="Purina" class="h-12 md:h-16 opacity-70 hover:opacity-100 transition-opacity">
          <img src="https://via.placeholder.com/150x60/cccccc/888888?text=Приют+Бирюлево" alt="Приют Бирюлево" class="h-12 md:h-16 opacity-70 hover:opacity-100 transition-opacity">
          <img src="https://via.placeholder.com/150x60/cccccc/888888?text=drug-sobaka.ru" alt="Drug Sobaka" class="h-12 md:h-16 opacity-70 hover:opacity-100 transition-opacity">
          <img src="https://via.placeholder.com/150x60/cccccc/888888?text=Друг+для+друга" alt="Друг для друга" class="h-12 md:h-16 opacity-70 hover:opacity-100 transition-opacity">
          <img src="https://via.placeholder.com/150x60/cccccc/888888?text=Искра" alt="Искра" class="h-12 md:h-16 opacity-70 hover:opacity-100 transition-opacity col-span-2 md:col-span-1 lg:col-auto justify-self-center">
        </div>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import AdCard from '../components/AdCard.vue';
import ArticleCard from '../components/ArticleCard.vue';

// Placeholder data - будет заменено данными из API
const recentAds = ref([
  { id: 1, imageUrl: 'https://via.placeholder.com/300x200/cccccc/888888?text=Dog+1', title: 'Найдена собака, отз...', description: 'На северном жилом массиве г. Ростов-на-Дону найден чёрный кобель, был в шлейке, ухожен, воспитан, порода похожа на...', location: 'Ростов-на-Дону', timeAgo: '1 день назад' },
  { id: 2, imageUrl: 'https://via.placeholder.com/300x200/cccccc/888888?text=Dog+2', title: 'Найдена собака, отз...', description: 'На северном жилом массиве г. Ростов-на-Дону найден чёрный кобель, был в шлейке, ухожен, воспитан, порода похожа на...', location: 'Ростов-на-Дону', timeAgo: '1 день назад' },
  { id: 3, imageUrl: 'https://via.placeholder.com/300x200/cccccc/888888?text=Dog+3', title: 'Найдена собака, отз...', description: 'На северном жилом массиве г. Ростов-на-Дону найден чёрный кобель, был в шлейке, ухожен, воспитан, порода похожа на...', location: 'Ростов-на-Дону', timeAgo: '1 день назад' },
  { id: 4, imageUrl: 'https://via.placeholder.com/300x200/cccccc/888888?text=Dog+4', title: 'Найдена собака, отз...', description: 'На северном жилом массиве г. Ростов-на-Дону найден чёрный кобель, был в шлейке, ухожен, воспитан, порода похожа на...', location: 'Ростов-на-Дону', timeAgo: '1 день назад' },
]);

const sideArticles = ref([
  { id: 1, imageUrl: 'https://via.placeholder.com/400x250/cccccc/888888?text=Dog+Article+1', title: 'Сколько раз в день нужно гулять с собакой', description: 'Сколько раз в день нужно гулять с собакой, зависит от возраста, породы и...', timeAgo: '1 год назад' },
  { id: 2, imageUrl: 'https://via.placeholder.com/400x250/cccccc/888888?text=Dog+Article+2', title: 'Сколько раз в день нужно гулять с собакой', description: 'Сколько раз в день нужно гулять с собакой, зависит от возраста, породы и...', timeAgo: '1 год назад' },
  { id: 3, imageUrl: 'https://via.placeholder.com/400x250/cccccc/888888?text=Dog+Article+3', title: 'Сколько раз в день нужно гулять с собакой', description: 'Сколько раз в день нужно гулять с собакой, зависит от возраста, породы и...', timeAgo: '1 год назад' },
]);

// В будущем:
// onMounted(async () => {
//   recentAds.value = await api.fetchRecentAds();
//   sideArticles.value = await api.fetchSideArticles();
// });
</script>