<template>
  <div class="bg-gray-50 min-h-screen">
    <div v-if="loading" class="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <p class="text-xl text-gray-500">Загрузка статьи...</p>
    </div>
    <div v-else-if="error" class="container mx-auto px-4 py-10 text-center">
      <p class="text-xl text-red-500 bg-red-100 p-6 rounded-lg shadow">Ошибка: {{ error }}</p>
      <router-link :to="{ name: 'Articles' }" class="mt-6 inline-block bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600">
        Ко всем статьям
      </router-link>
    </div>
    <div v-else-if="article" class="article-detail-page">
      <!-- Изображение и контент теперь внутри одного контейнера с max-w-3xl -->
      <div class="container mx-auto max-w-3xl px-4 pt-8 md:pt-12">
        <!-- Главное изображение статьи (ПЕРЕМЕЩЕНО И ИЗМЕНЕНО) -->
        <div v-if="article.main_image_url" class="mb-6 md:mb-8 rounded-lg overflow-hidden shadow-lg">
          <img :src="article.main_image_url" :alt="article.title" class="w-full h-auto object-cover">
          <!-- Высота будет определяться пропорциями изображения, h-auto важно -->
        </div>
        <div v-else-if="!article.main_image_url && !loading" class="mb-6 md:mb-8 h-[200px] bg-gray-200 flex items-center justify-center text-gray-500 rounded-lg">
          Изображение отсутствует
        </div>

        <!-- Заголовок статьи -->
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-800 mb-6 text-center md:text-left">
          {{ article.title }}
        </h1>

        <!-- Информация об авторе и дата -->
        <div class="flex items-center mb-8 text-sm text-gray-600">
          <img
            v-if="article.author && article.author.avatar_url"
            :src="article.author.avatar_url"
            :alt="article.author.display_name"
            class="w-10 h-10 md:w-12 md:h-12 rounded-full mr-3 object-cover"
          >
          <img
            v-else-if="article.author"
            src="/images/no-image-data.png"
            alt="Аватар по умолчанию"
            class="w-10 h-10 md:w-12 md:h-12 rounded-full mr-3 object-cover bg-gray-200"
          >
          <div>
            <p v-if="article.author" class="font-semibold text-gray-800">
              {{ article.author.display_name }}
            </p>
            <p v-else class="font-semibold text-gray-800">
              Автор неизвестен
            </p>
            <p>{{ formattedPublicationDate }}</p>
          </div>
        </div>

        <!-- Содержимое статьи -->
        <div
          class="prose prose-sm sm:prose-base lg:prose-lg max-w-none text-gray-700 leading-relaxed article-content pb-8 md:pb-12"
          v-html="article.content"
        ></div>
      </div> <!-- Конец контейнера max-w-3xl -->
    </div>
    <div v-else class="flex justify-center items-center min-h-[calc(100vh-200px)]">
       <p class="text-xl text-gray-500">Статья не найдена.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router'; // useRoute для доступа к текущему маршруту
import axios from 'axios';
import type { ArticleDetail, Author } from '../types'; // Предполагаем, что типы в types/index.ts
import { formatDate } from '../utils/time'; // Импортируем нашу функцию форматирования

const props = defineProps<{
  id: string | number; // id будет передан из router-view props: true
}>();

const article = ref<ArticleDetail | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const route = useRoute(); // Для отслеживания изменений id, если это необходимо

const fetchArticleDetail = async (articleId: string | number) => {
  loading.value = true;
  error.value = null;
  article.value = null;
  try {
    const response = await axios.get<ArticleDetail>(`${API_BASE_URL}/articles/${articleId}/`);
    article.value = response.data;
  } catch (err) {
    console.error(`Ошибка при загрузке статьи ${articleId}:`, err);
    if (axios.isAxiosError(err)) {
      if (err.response && err.response.status === 404) {
        error.value = "Статья не найдена.";
      } else {
        error.value = `Не удалось загрузить статью: ${err.message}.`;
      }
    } else {
      error.value = "Произошла неизвестная ошибка.";
    }
  } finally {
    loading.value = false;
  }
};

const formattedPublicationDate = computed(() => {
  return article.value ? formatDate(article.value.publication_date) : '';
});

onMounted(() => {
  fetchArticleDetail(props.id);
});

// Если вы хотите перезагружать данные при изменении параметра id без полной перезагрузки компонента
// (например, если на странице есть ссылки на другие статьи)
watch(() => props.id, (newId) => {
  if (newId) {
    fetchArticleDetail(newId);
  }
});
</script>

<style>
/* Стили для контента, генерируемого v-html */
.article-content h1, .article-content h2, .article-content h3, .article-content h4 {
  @apply font-bold text-gray-800 mb-4 mt-6;
}
.article-content h1 { @apply text-3xl sm:text-4xl; }
.article-content h2 { @apply text-2xl sm:text-3xl; } /* Пример из макета "Как назначают лечение" */
.article-content h3 { @apply text-xl sm:text-2xl; }
.article-content h4 { @apply text-lg sm:text-xl; }

.article-content p {
  @apply mb-4 text-gray-700;
}

.article-content a {
  @apply text-green-600 hover:text-green-700 underline;
}

.article-content ul, .article-content ol {
  @apply list-inside mb-4 pl-4;
}
.article-content ul { @apply list-disc; }
.article-content ol { @apply list-decimal; }

.article-content li {
  @apply mb-2;
}

.article-content blockquote {
  @apply border-l-4 border-gray-300 pl-4 py-2 my-4 italic text-gray-600;
}

.article-content img {
  @apply rounded-lg my-6 shadow-sm max-w-full h-auto mx-auto;
}

</style>