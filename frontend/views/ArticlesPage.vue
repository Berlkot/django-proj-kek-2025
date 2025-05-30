<template>
  <div class="bg-gray-50 min-h-screen">

    <section class="bg-gray-700 text-white py-10 md:py-12">
      <div class="container mx-auto px-4 text-center">
        <h1 class="text-3xl md:text-4xl font-bold">Статьи о питомцах</h1>
        <p class="text-lg mt-2 text-gray-300">Полезная информация, советы по уходу и многое другое.</p>
      </div>
    </section>


    <div class="container mx-auto px-4 py-8 md:py-10">

      <div class="mb-6 md:mb-8">

        <div class="flex flex-col gap-4">

          <div class="w-full">
            <form @submit.prevent="applySearchAndFilter" class="flex">
              <input type="text" v-model="searchQueryInput" placeholder="Поиск статей..."
                class="flex-grow p-3 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500" />
              <button type="submit"
                class="bg-green-500 text-white px-5 py-3 rounded-r-md hover:bg-green-600 flex items-center justify-center"
                aria-label="Поиск">
                <font-awesome-icon :icon="['fas', 'search']" class="h-5 w-5 md:mr-2" />
                <span class="hidden md:inline">Поиск</span>
              </button>
            </form>
          </div>


          <div class="w-full">

            <div class="hidden md:flex space-x-2 flex-wrap" role="group" aria-label="Категории статей">

              <button @click="selectCategory('all')" :class="getCategoryButtonClass('all')">
                Все
              </button>
              <template v-for="category in categories" :key="category ? category.id : 'fallback-key-' + Math.random()">
                <button v-if="category && category.slug && category.name" @click="selectCategory(category.slug)"
                  :class="getCategoryButtonClass(category.slug)">
                  {{ category.name }}
                </button>
              </template>
            </div>

            <div class="md:hidden">
              <label for="category-select" class="sr-only">Выберите категорию</label>
              <select id="category-select" v-model="selectedCategorySlug" @change="applySearchAndFilter"
                class="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500 bg-white">
                <option value="all">Все категории</option>
                <template v-for="category in categories"
                  :key="category ? category.id : 'fallback-key-select-' + Math.random()">
                  <option v-if="category && category.slug && category.name" :value="category.slug">
                    {{ category.name }}
                  </option>
                </template>
              </select>
            </div>
          </div>
          <div class="text-right mb-4" v-if="authStore.isAuthenticated && authStore.user?.is_staff">
            <router-link :to="{ name: 'ArticleCreate' }"
              class="bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-md">
              Создать статью
            </router-link>
          </div>
        </div>
      </div>


      <div v-if="loading" class="text-center py-10 text-gray-500 text-lg">
        Загрузка статей...
      </div>
      <div v-else-if="error" class="text-center py-10 text-red-500 bg-red-50 p-4 rounded-md">
        Ошибка при загрузке статей: {{ error }}
      </div>
      <div v-else-if="articles.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
        <template v-for="article in articles" :key="article ? article.id : 'article-fallback-' + Math.random()">
          <ArticleGridCard v-if="article" :article="article" />
        </template>
      </div>
      <div v-else class="text-center py-10 text-gray-600 text-lg">
        Статьи не найдены. Попробуйте изменить условия поиска.
      </div>


      <div v-if="!loading && totalPages > 1"
        class="mt-8 md:mt-12 flex justify-center items-center space-x-1 sm:space-x-2">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
          class="px-3 py-2 sm:px-4 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
          < Назад </button>
            <button v-for="pageNumber in paginationNumbers" :key="pageNumber" @click="changePage(pageNumber)"
              :class="['px-3 py-2 sm:px-4 border rounded-md text-sm', currentPage === pageNumber ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50']"
              :disabled="pageNumber === '...'">
              {{ pageNumber }}
            </button>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages"
              class="px-3 py-2 sm:px-4 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-sm">
              Вперед >
            </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import ArticleGridCard from '../components/ArticleGridCard.vue';
import type { ArticleCategory } from '../types'
import { useAuthStore } from '../stores/auth';

interface Article {
  id: number;
  title: string;
  excerpt: string;
  publication_date: string;
  author_name: string | null;
  main_image_url: string | null;
  categories?: ArticleCategory[];
}

interface PaginatedArticlesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Article[];
}
const authStore = useAuthStore();
const articles = ref<Article[]>([]);
const categories = ref<ArticleCategory[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const searchQueryInput = ref('');
const currentSearchQuery = ref('');
const selectedCategorySlug = ref<string>('all');
const currentPage = ref(1);

const totalPages = ref(1);
const itemsPerPage = 9;

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const router = useRouter();
const route = useRoute();

const lastFetchedPage = ref(1);
const lastFetchedSearch = ref('');
const lastFetchedCategory = ref('all');

const fetchArticles = async (page: number, search: string, category: string) => {
  loading.value = true;
  error.value = null;
  try {
    const params: Record<string, any> = {
      page: page,
      page_size: itemsPerPage,
    };
    if (search) {
      params.search = search;
    }
    if (category && category !== 'all') {
      params.category = category;
    }

    const response = await axios.get<PaginatedArticlesResponse>(`${API_BASE_URL}/articles/`, { params });

    articles.value = response.data.results ? response.data.results.filter(art => art !== null && art !== undefined) : [];
    totalPages.value = Math.ceil(response.data.count / itemsPerPage);


    currentPage.value = page;
    currentSearchQuery.value = search;
    selectedCategorySlug.value = category;


    lastFetchedPage.value = page;
    lastFetchedSearch.value = search;
    lastFetchedCategory.value = category;

  } catch (err) {
    console.error("Ошибка при загрузке статей:", err);
    error.value = axios.isAxiosError(err) ? `Не удалось загрузить статьи: ${err.message}.` : "Произошла неизвестная ошибка.";
    articles.value = [];
    totalPages.value = 1;


  } finally {
    loading.value = false;
  }
};

const fetchCategories = async () => {
  try {
    const response = await axios.get<ArticleCategory[]>(`${API_BASE_URL}/article-categories/`);
    categories.value = response.data;
  } catch (err) {
    console.error("Ошибка при загрузке категорий:", err);

  }
};

const updateRouteQuery = () => {
  const query: Record<string, string | number> = {};

  if (currentPage.value > 1) query.page = currentPage.value;
  if (currentSearchQuery.value) query.search = currentSearchQuery.value;
  if (selectedCategorySlug.value && selectedCategorySlug.value !== 'all') {
    query.category = selectedCategorySlug.value;
  }

  router.push({ query: query });
};

const applySearchAndFilter = () => {
  currentPage.value = 1;
  currentSearchQuery.value = searchQueryInput.value;

  updateRouteQuery();
};

const selectCategory = (slug: string) => {
  selectedCategorySlug.value = slug;

  currentPage.value = 1;
  updateRouteQuery();
};

const changePage = (page: number) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page;

    updateRouteQuery();
  }
};

const getCategoryButtonClass = (slug: string) => {
  return [
    'px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150',
    selectedCategorySlug.value === slug ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
  ];
};

const paginationNumbers = computed(() => {
  const delta = 1;
  const range = [];
  const rangeWithDots: (number | string)[] = [];
  let l: number | undefined;

  range.push(1);
  for (let i = currentPage.value - delta; i <= currentPage.value + delta; i++) {
    if (i >= 2 && i < totalPages.value) {
      range.push(i);
    }
  }
  if (totalPages.value > 1) {
    range.push(totalPages.value);
  }

  range.forEach((i) => {
    if (l !== undefined) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  });

  return rangeWithDots.filter(page => page !== '...' || (page === '...' && rangeWithDots[rangeWithDots.indexOf(page) - 1] !== '...'));
});

watch(() => route.query, (newQuery, oldQuery) => {
  const pageFromQuery = newQuery.page ? parseInt(newQuery.page as string, 10) : 1;
  const searchFromQuery = (newQuery.search as string) || '';
  const categoryFromQuery = (newQuery.category as string) || 'all';


  if (searchFromQuery !== searchQueryInput.value) {
    searchQueryInput.value = searchFromQuery;
  }




  if (pageFromQuery !== lastFetchedPage.value ||
    searchFromQuery !== lastFetchedSearch.value ||
    categoryFromQuery !== lastFetchedCategory.value) {
    fetchArticles(pageFromQuery, searchFromQuery, categoryFromQuery);
  }
},
  { immediate: false }
);

onMounted(() => {
  fetchCategories();

  const initialPage = route.query.page ? parseInt(route.query.page as string, 10) : 1;
  const initialSearch = (route.query.search as string) || '';
  const initialCategory = (route.query.category as string) || 'all';

  searchQueryInput.value = initialSearch;

  fetchArticles(initialPage, initialSearch, initialCategory);
});

</script>

<style scoped></style>
