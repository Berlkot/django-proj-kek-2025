<template>
  <div class="bg-gray-100 min-h-screen">

    <div
      class="bg-white md:bg-transparent shadow-sm md:shadow-none sticky top-[64px] md:static z-30 md:pt-6 pb-3 md:pb-0">
      <div class="container mx-auto px-4">
        <div class="md:hidden flex items-center justify-between mb-3 pt-3">
          <h1 class="text-xl font-semibold">Объявления</h1>
          <button @click="isMobileFilterOpen = true" class="p-2 text-gray-600 hover:text-green-500">
            <font-awesome-icon :icon="['fas', 'filter']" class="w-5 h-5" />
            <span class="ml-1">Фильтры</span>
          </button>
        </div>
        <div class="flex items-center space-x-2 md:hidden">
          <input type="text" v-model="searchQueryInput" placeholder="Поиск животных..." @keyup.enter="applySearch"
            class="flex-grow p-3 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500" />
          <button @click="applySearch" class="bg-green-500 text-white px-4 py-3 rounded-r-md hover:bg-green-600">
            <font-awesome-icon :icon="['fas', 'search']" />
          </button>
        </div>
      </div>
    </div>


    <div class="container mx-auto px-4 py-6 md:py-8">
      <div class="mb-6 text-right"
        v-if="authStore.isAuthenticated && (authStore.user?.is_staff || authStore.user?.role_permissions?.can_create_advertisement)">
        <router-link :to="{ name: 'AdvertisementCreate' }"
          class="inline-flex items-center bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-md shadow-sm transition-colors">
          <font-awesome-icon :icon="['fas', 'plus-circle']" class="mr-2" />
          Создать объявление
        </router-link>
      </div>
      <div class="flex flex-col md:flex-row gap-6 md:gap-8">

        <div class="hidden md:block md:w-1/4 lg:w-1/5">
          <FilterSidebar :options="filterOptions" v-model="selectedFilters" @apply-filters="handleApplyFilters"
            @reset-filters="handleResetFilters" />
        </div>



        <div class="w-full md:w-3/4 lg:w-4/5">

          <div class="hidden md:flex justify-between items-center mb-6">
            <h1 class="text-2xl lg:text-3xl font-bold text-gray-800">Объявления</h1>
            <div class="flex items-center">
              <span class="text-sm text-gray-600 mr-2">Найдено: {{ totalAdsCount }}</span>
              <select v-model="currentOrdering" @change="applySorting"
                class="p-2 border border-gray-300 rounded-md text-sm focus:ring-green-500 focus:border-green-500">
                <option value="-publication_date">Сначала новые</option>
                <option value="publication_date">Сначала старые</option>
                <option value="animal__name">По имени (А-Я)</option>
                <option value="-animal__name">По имени (Я-А)</option>
              </select>
            </div>
          </div>

          <div class="hidden md:block mb-6">
            <div class="flex max-w-xl">
              <input type="text" v-model="searchQueryInput" placeholder="Поиск по названию, описанию, кличке..."
                @keyup.enter="applySearch"
                class="flex-grow p-3 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500" />
              <button @click="applySearch" class="bg-green-500 text-white px-6 py-3 rounded-r-md hover:bg-green-600">
                Поиск
              </button>
            </div>
          </div>




          <div v-if="loadingAds" class="text-center py-10">
            <p class="text-gray-500 text-lg">Загрузка объявлений...</p>
          </div>
          <div v-else-if="errorAds" class="text-center py-10 bg-red-50 p-4 rounded-md">
            <p class="text-red-500">Ошибка: {{ errorAds }}</p>
          </div>
          <div v-else-if="advertisements.length > 0"
            class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
            <AdCard v-for="ad in advertisements" :key="ad.id" :id="ad.id"
              :image-url="ad.first_photo_url || '/static/images/no-image-data.png'" :title="ad.title"
              :description="ad.short_description" :location="ad.location" :time-ago="formatTimeAgo(ad.publication_date)"
              :ad-type="ad.status" :species-name="ad.animal.species" />
          </div>
          <div v-else class="text-center py-16 text-gray-600">
            <h3 class="text-xl font-semibold mb-2">Объявления не найдены</h3>
            <p>Попробуйте изменить критерии поиска или сбросить фильтры.</p>
          </div>


          <div v-if="!loadingAds && totalPages > 1"
            class="mt-8 md:mt-12 flex justify-center items-center space-x-1 sm:space-x-2">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
              class="px-3 py-2 sm:px-4 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50">
              < Назад</button>
                <button v-for="pageNumber in paginationNumbers" :key="pageNumber" @click="changePage(pageNumber)"
                  :class="['px-3 py-2 sm:px-4 border rounded-md', currentPage === pageNumber ? 'bg-green-500 text-white border-green-500' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50']"
                  :disabled="pageNumber === '...'">{{ pageNumber }}</button>
                <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages"
                  class="px-3 py-2 sm:px-4 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50">Вперед
                  ></button>
          </div>
        </div>
      </div>
    </div>
    <MobileFilterModal v-model:isOpen="isMobileFilterOpen" :options="filterOptions" :modelValue="selectedFilters"
      @apply-filters="handleApplyFiltersFromModal" @reset-filters="handleResetFilters" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import AdCard from '../components/AdCard.vue';
import FilterSidebar from '../components/FilterSidebar.vue';
import MobileFilterModal from '../components/MobileFilterModal.vue';
import { formatTimeAgo } from '../utils/time';
import { useAuthStore } from '../stores/auth';
import type { Advertisement, PaginatedAdvertisementsResponse, FilterOptions, SelectedFilters, Breed } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const advertisements = ref<Advertisement[]>([]);
const loadingAds = ref(true);
const errorAds = ref<string | null>(null);
const totalAdsCount = ref(0);
const totalPages = ref(1);
const currentPage = ref(1);
const itemsPerPage = 12;
const authStore = useAuthStore();

const filterOptions = ref<FilterOptions>({
  regions: [], species: [], ad_statuses: [], colors: [],
  genders: [], age_categories: [], breeds: [],
});

const defaultFilters: SelectedFilters = {
  region: null, age_category: null, ad_status: null,
  species: null, breed: null, color: null, gender: null,
  publication_date_after: null, publication_date_before: null,
};
const selectedFilters = ref<SelectedFilters>({ ...defaultFilters });

const searchQueryInput = ref('');
const currentSearchQuery = ref('');
const currentOrdering = ref('-publication_date');

const isMobileFilterOpen = ref(false);

const router = useRouter();
const route = useRoute();

let initialLoadDone = false;

const fetchFilterOptions = async () => {
  try {
    const response = await axios.get<FilterOptions>(`${API_BASE_URL}/filter-options/`);
    filterOptions.value = response.data;
  } catch (err) {
    console.error("Ошибка загрузки опций фильтров:", err);
  }
};

const fetchAdvertisements = async () => {
  loadingAds.value = true;
  errorAds.value = null;
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: itemsPerPage,
      ordering: currentOrdering.value,
    };
    if (currentSearchQuery.value) {
      params.search = currentSearchQuery.value;
    }
    for (const key in selectedFilters.value) {
      const filterKey = key as keyof SelectedFilters;
      if (selectedFilters.value[filterKey] !== null && selectedFilters.value[filterKey] !== '') {
        params[filterKey] = selectedFilters.value[filterKey];
      }
    }

    const response = await axios.get<PaginatedAdvertisementsResponse>(`${API_BASE_URL}/advertisements/`, { params });
    advertisements.value = response.data.results;
    totalAdsCount.value = response.data.count;
    totalPages.value = Math.ceil(response.data.count / itemsPerPage);
    initialLoadDone = true;
  } catch (err) {
    errorAds.value = axios.isAxiosError(err) ? `Ошибка: ${err.message}` : "Неизвестная ошибка";
    initialLoadDone = true;
  } finally {
    loadingAds.value = false;
  }
};


const updateRouteQuery = () => {
  const query: Record<string, string | number> = {};

  if (currentPage.value > 1) query.page = currentPage.value;
  if (currentSearchQuery.value) query.search = currentSearchQuery.value;
  if (currentOrdering.value !== '-publication_date') query.ordering = currentOrdering.value;

  for (const key in selectedFilters.value) {
    const filterKey = key as keyof SelectedFilters;
    const filterValue = selectedFilters.value[filterKey];
    if (filterValue !== null && filterValue !== '') {
      query[filterKey] = String(filterValue);
    }
  }
  router.replace({ query });
};

const applySearch = () => {
  currentSearchQuery.value = searchQueryInput.value;
  currentPage.value = 1;
  updateRouteQuery(); 
};

const applySorting = () => {
  currentPage.value = 1;
  updateRouteQuery();
};

const handleApplyFilters = (newFilterValues: SelectedFilters) => {
  selectedFilters.value = { ...newFilterValues };
  currentPage.value = 1;
  updateRouteQuery();
};

const handleApplyFiltersFromModal = (filtersFromModal: SelectedFilters) => {
  handleApplyFilters(filtersFromModal);
  isMobileFilterOpen.value = false;
};

const handleResetFilters = () => {
  searchQueryInput.value = '';
  currentPage.value = 1;
  currentSearchQuery.value = '';
  currentOrdering.value = '-publication_date';
  selectedFilters.value = { ...defaultFilters };
  updateRouteQuery();
  isMobileFilterOpen.value = false;
};

const changePage = (page: number | string) => {
  if (typeof page === 'string' || page < 1 || page > totalPages.value || page === currentPage.value) return;
  currentPage.value = page;
  updateRouteQuery();
};

watch(
  () => route.query,
  async (newQuery) => {
    const newPage = newQuery.page ? parseInt(newQuery.page as string, 10) : 1;
    const newSearch = (newQuery.search as string) || '';
    const newOrdering = (newQuery.ordering as string) || '-publication_date';

    const newFiltersStateFromQuery: SelectedFilters = { ...defaultFilters };
    for (const key in defaultFilters) {
      const filterKey = key as keyof SelectedFilters;
      const queryValue = newQuery[filterKey] as string | undefined;
      if (queryValue !== undefined && queryValue !== null && queryValue !== '') {
        if (filterKey === 'age_category' || filterKey === 'gender' || filterKey === 'publication_date_after' || filterKey === 'publication_date_before') {
          newFiltersStateFromQuery[filterKey] = queryValue;
        } else {
          const numValue = parseInt(queryValue, 10);
          newFiltersStateFromQuery[filterKey] = isNaN(numValue) ? null : numValue;
        }
      } else {
        newFiltersStateFromQuery[filterKey] = null;
      }
    }
    
    if (currentPage.value !== newPage) currentPage.value = newPage;
    if (currentSearchQuery.value !== newSearch) currentSearchQuery.value = newSearch;
    if (searchQueryInput.value !== newSearch) searchQueryInput.value = newSearch;
    if (currentOrdering.value !== newOrdering) currentOrdering.value = newOrdering;
    if (JSON.stringify(selectedFilters.value) !== JSON.stringify(newFiltersStateFromQuery)) {
        selectedFilters.value = newFiltersStateFromQuery;
    }
    

    if (initialLoadDone || Object.keys(newQuery).length > 0) {
        await fetchAdvertisements();
    } else if (!initialLoadDone && Object.keys(newQuery).length === 0) {
        await fetchAdvertisements();
    }
  },
  { deep: true, immediate: true } 
);


onMounted(async () => {
  await fetchFilterOptions();
});

const availableBreedsForFilter = computed(() => { 
    if (!selectedFilters.value.species || !filterOptions.value.breeds.length) {
        return [];
    }
    return filterOptions.value.breeds.filter(b => b.species_id === selectedFilters.value.species);
});

watch(() => selectedFilters.value.species, (newSpeciesId, oldSpeciesId) => {
    if (newSpeciesId !== oldSpeciesId && selectedFilters.value.breed !== null) {
        const currentBreedIsValidForNewSpecies = availableBreedsForFilter.value.some(
            (breed) => breed.id === selectedFilters.value.breed
        );
        if (!currentBreedIsValidForNewSpecies) {
            selectedFilters.value.breed = null;
        }
    }
});

const paginationNumbers = computed(() => {
  const delta = 1;
  const range: (number | string)[] = [];
  let l: number | undefined;
  range.push(1);
  for (let i = currentPage.value - delta; i <= currentPage.value + delta; i++) {
    if (i >= 2 && i < totalPages.value) range.push(i);
  }
  if (totalPages.value > 1) range.push(totalPages.value);
  range.forEach(i => {
    if (typeof i === 'number') {
      if (l !== undefined) {
        if (i - l === 2) range.push(l + 1);
        else if (i - l !== 1) range.push('...');
      }
      range.push(i);
      l = i;
    } else {
      range.push(i);
      l = undefined;
    }
  });

  const result: (number | string)[] = [];
  const P = currentPage.value;
  const T = totalPages.value;
  if (T <= 7) { for (let i = 1; i <= T; i++) result.push(i); }
  else {
    result.push(1);
    if (P > 3) result.push('...');
    if (P === T && T > 3) result.push(P - 2);
    if (P > 2) result.push(P - 1);
    if (P !== 1 && P !== T) result.push(P);
    if (P < T - 1) result.push(P + 1);
    if (P === 1 && T > 3) result.push(P + 2);
    if (P < T - 2) result.push('...');
    if (T > 1) result.push(T);
  }
  return result.filter((item, index, self) => item !== '...' || (item === '...' && self[index - 1] !== '...'));
});


import { library } from '@fortawesome/fontawesome-svg-core';
import { faFilter } from '@fortawesome/free-solid-svg-icons';
library.add(faFilter);

</script>