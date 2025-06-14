<template>
  <div>
    <section class="bg-gray-700 text-white pt-16 md:pt-24 pb-0 relative overflow-hidden">
      <div class="container mx-auto px-4 flex flex-col md:flex-row items-center relative z-10">
        <div class="md:w-1/2 text-center md:text-left mb-10 md:mb-0 md:pr-8">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">Поиск животных</h1>
          <p class="text-lg mb-8">Найди или помоги другому найти своего любимца</p>
          <form @submit.prevent="performSearch" class="flex max-w-md mx-auto md:mx-0">
            <input
              type="text"
              v-model="searchQueryHomepage"
              placeholder="Поиск животных..."
              class="flex-grow p-3 border border-gray-300 rounded-l-md focus:ring-green-500 focus:border-green-500 text-gray-800"
            />
            <button
              type="submit"
              class="bg-green-500 text-white px-6 py-3 rounded-r-md hover:bg-green-600 flex items-center justify-center"
            >
              <font-awesome-icon :icon="['fas', 'search']" class="mr-2" />
              Поиск
            </button>
          </form>
        </div>
        <div class="md:w-1/2 flex justify-center md:justify-end self-end">
          <img
            src="/images/hero-pets.png"
            alt="Собака и кошка"
            class="max-w-full h-auto md:max-w-lg lg:max-w-xl"
          />
        </div>
      </div>
    </section>
    <section class="py-10 md:py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-6 md:mb-8">
          <h2 class="text-2xl md:text-3xl font-bold text-gray-800">Последние объявления</h2>
          <router-link
            :to="{ name: 'Advertisements' }"
            class="text-green-600 hover:text-green-700 font-semibold flex items-center text-sm md:text-base"
          >
            Посмотреть все
            <font-awesome-icon :icon="['fas', 'chevron-right']" class="ml-1 w-3 h-3" />
          </router-link>
        </div>
        <div v-if="loadingAds" class="text-center text-gray-500">Загрузка объявлений...</div>
        <div
          v-else-if="recentAds.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6"
        >
          <AdCard
            v-for="ad in recentAds"
            :key="ad.id"
            :id="ad.id"
            :image-url="ad.first_photo_url || '/static/images/no-image-data.png'"
            :title="ad.title"
            :description="ad.short_description"
            :location="ad.location"
            :time-ago="formatTimeAgo(ad.publication_date)"
            :ad-type="ad.status_name"
            :species-name="ad.species_name"
          />
        </div>
        <div
          v-else-if="!loadingAds && recentAds.length === 0"
          class="text-center text-gray-500 py-8"
        >
          Нет доступных объявлений.
        </div>
        <div v-if="errorAds" class="text-center text-red-500 mt-4">{{ errorAds }}</div>
        <div class="mt-8 text-center">
          <router-link
            :to="{ name: 'Advertisements' }"
            class="inline-block bg-green-500 text-white px-8 py-3 rounded-md hover:bg-green-600 font-semibold"
          >
            Больше объявлений
          </router-link>
        </div>
      </div>
    </section>
    <section class="py-10 md:py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-6 md:mb-8">
          <h2 class="text-2xl md:text-3xl font-bold text-gray-800">Самые активные регионы</h2>
          <router-link
            :to="{ name: 'Advertisements' }"
            class="text-green-600 hover:text-green-700 font-semibold flex items-center text-sm md:text-base"
          >
            Все объявления
            <font-awesome-icon :icon="['fas', 'chevron-right']" class="ml-1 w-3 h-3" />
          </router-link>
        </div>

        <div v-if="loadingRegions" class="text-center text-gray-500">Загрузка регионов...</div>
        <div v-else-if="topRegions.length > 0" class="bg-gray-50 p-4 sm:p-6 rounded-lg shadow">
          <ol class="space-y-3">
            <router-link
              v-for="(region, index) in topRegions"
              :key="region.id"
              :to="{ name: 'Advertisements', query: { region: region.id } }"
              custom
              v-slot="{ navigate, isActive, isExactActive }"
            >
              <li
                @click="navigate"
                @keypress.enter="navigate"
                role="link"
                tabindex="0"
                :class="[
                  'flex items-center space-x-3 p-3 bg-white rounded-md shadow-sm hover:shadow-lg transition-all duration-200 cursor-pointer focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50',
                ]"
              >
                <span
                  class="flex-shrink-0 w-8 h-8 bg-green-500 text-white text-sm font-semibold rounded-full flex items-center justify-center"
                >
                  {{ index + 1 }}
                </span>
                <div class="flex-grow min-w-0">
                  <span
                    class="text-base sm:text-lg font-medium text-gray-800 group-hover:text-green-600 truncate block"
                    :title="region.name"
                  >
                    {{ region.name }}
                  </span>
                  <p class="text-xs sm:text-sm text-gray-500">Объявлений: {{ region.ad_count }}</p>
                </div>
                <button
                  @click.stop="toggleFavorite(region.id)"
                  class="flex-shrink-0 p-2 text-gray-400 hover:text-red-500 rounded-full hover:bg-red-50 transition-colors z-10 relative"
                  title="Добавить в избранное (пока не работает)"
                  aria-label="Добавить регион в избранное"
                >
                  <font-awesome-icon :icon="['fa', 'heart']" class="w-5 h-5" />
                </button>
              </li>
            </router-link>
          </ol>
        </div>
        <div
          v-else-if="!loadingRegions && topRegions.length === 0"
          class="text-center text-gray-500 py-8"
        >
          Нет данных по активности регионов.
        </div>
        <div v-if="errorRegions" class="text-center text-red-500 mt-4">{{ errorRegions }}</div>
      </div>
    </section>

    <section class="py-10 md:py-12 bg-gray-100">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center mb-6 md:mb-8">
          <h2 class="text-2xl md:text-3xl font-bold text-gray-800">Статьи о питомцах</h2>
          <router-link
            :to="{ name: 'Articles' }"
            class="text-green-600 hover:text-green-700 font-semibold flex items-center text-sm md:text-base"
          >
            Посмотреть все
            <font-awesome-icon :icon="['fas', 'chevron-right']" class="ml-1 w-3 h-3" />
          </router-link>
        </div>

        <div v-if="loadingArticles" class="text-center text-gray-500">Загрузка статей...</div>
        <div
          v-else-if="mainArticle || sideArticles.length > 0"
          class="flex flex-col lg:flex-row lg:items-stretch gap-6 md:gap-8"
        >
          <div v-if="mainArticle && mainArticleForGridCard" class="w-full lg:w-2/3">
            <ArticleGridCard :article="mainArticleForGridCard" :large="true" class="h-full" />
          </div>

          <div
            v-if="sideArticles.length > 0"
            class="w-full lg:w-1/3 flex flex-col space-y-4 md:space-y-6"
          >
            <ArticleGridCard
              v-for="article in sideArticlesForGridCard"
              :key="article.id"
              :article="article"
              class="h-full"
            />
          </div>
        </div>
        <div
          v-else-if="!loadingArticles && !mainArticle && sideArticles.length === 0"
          class="text-center text-gray-500 py-8"
        >
          Нет доступных статей.
        </div>
        <div v-if="errorArticles" class="text-center text-red-500 mt-4">{{ errorArticles }}</div>
        <div class="mt-8 text-center">
          <router-link
            :to="{ name: 'Articles' }"
            class="inline-block bg-green-500 text-white px-8 py-3 rounded-md hover:bg-green-600 font-semibold"
          >
            Больше статей
          </router-link>
        </div>
      </div>
    </section>

    <section class="py-10 md:py-12 bg-white">
      <div class="container mx-auto px-4">
        <div class="flex flex-col lg:flex-row items-center gap-6 md:gap-8">
          <div class="w-full lg:w-1/2 text-center lg:text-left">
            <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-3 md:mb-4">Приюты</h2>
            <p class="text-gray-700 mb-3 md:mb-4 text-sm md:text-base">
              Зачем куда-to далеко ходить или спрашивать у знакомых.
            </p>
            <p class="text-gray-700 mb-6 md:mb-8 text-sm md:text-base">
              Легко найдите приют на интерактивной карте в шаге от вашего дома
            </p>
            <router-link
              to="/shelters"
              class="inline-block bg-white text-green-600 border border-green-600 px-6 py-3 rounded-md hover:bg-green-50 font-semibold"
            >
              О приютах
            </router-link>
          </div>
          <div class="w-full lg:w-1/2">
            <img
              src="/images/map-placeholder.png"
              alt="Карта приютов"
              class="w-full rounded-lg shadow-md max-h-[300px] md:max-h-[400px] object-cover"
            />
          </div>
        </div>
      </div>
    </section>

    <section class="py-10 md:py-12 bg-gray-100">
      <div class="container mx-auto px-4">
        <div
          class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-6 md:gap-8 items-center justify-items-center"
        >
          <img
            src="/images/partners/purina.png"
            alt="Purina"
            class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity"
          />
          <img
            src="/images/partners/birulevo.png"
            alt="Приют Бирюлево"
            class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity"
          />
          <img
            src="/images/partners/drug-sobaka.png"
            alt="Drug Sobaka"
            class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity"
          />
          <img
            src="/images/partners/drug-dlya-druga.png"
            alt="Друг для друга"
            class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity"
          />

          <img
            src="/images/partners/iskra.png"
            alt="Искра"
            class="h-10 md:h-12 opacity-70 hover:opacity-100 transition-opacity col-span-2 sm:col-span-1"
          />
        </div>
      </div>
    </section>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import AdCard from '../components/AdCard.vue'
import ArticleGridCard from '../components/ArticleGridCard.vue'
import { formatTimeAgo } from '../utils/time'
import { useRouter } from 'vue-router'
import type { ArticleCategory } from '../types'

interface HomePageAd {
  id: number
  title: string
  short_description: string
  publication_date: string
  first_photo_url: string | null
  location: string
  species_name: string
  status_name?: string
}

interface HomePageArticle {
  id: number
  title: string
  excerpt: string
  publication_date: string
  author_name: string | null
  main_image_url: string | null
}

interface ArticleForGridCard {
  id: number
  title: string
  excerpt: string
  publication_date: string
  main_image_url: string | null
  categories?: ArticleCategory[]
}

interface TopRegion {
  id: number
  name: string
  ad_count: number
}

const recentAds = ref<HomePageAd[]>([])
const mainArticle = ref<HomePageArticle | null>(null)
const sideArticles = ref<HomePageArticle[]>([])

const loadingAds = ref(true)
const errorAds = ref<string | null>(null)
const loadingArticles = ref(true)
const errorArticles = ref<string | null>(null)

const topRegions = ref<TopRegion[]>([])
const loadingRegions = ref(true)
const errorRegions = ref<string | null>(null)

const searchQueryHomepage = ref('')
const router = useRouter()

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const performSearch = () => {
  if (searchQueryHomepage.value.trim()) {
    router.push({
      name: 'Advertisements',
      query: { search: searchQueryHomepage.value.trim() }, 
    })
  } else {
    router.push({ name: 'Advertisements' })
  }
}

const mainArticleForGridCard = computed((): ArticleForGridCard | undefined => {
  if (!mainArticle.value) return undefined
  return {
    id: mainArticle.value.id,
    title: mainArticle.value.title,
    excerpt: mainArticle.value.excerpt,
    publication_date: mainArticle.value.publication_date,
    main_image_url: mainArticle.value.main_image_url,
  }
})

const sideArticlesForGridCard = computed((): ArticleForGridCard[] => {
  return sideArticles.value.map((article) => ({
    id: article.id,
    title: article.title,
    excerpt: article.excerpt,
    publication_date: article.publication_date,
    main_image_url: article.main_image_url,
  }))
})

const fetchData = async () => {
  loadingAds.value = true
  loadingArticles.value = true
  errorAds.value = null
  errorArticles.value = null

  try {
    const response = await axios.get<{
      recent_ads: HomePageAd[]
      main_article: HomePageArticle | null
      side_articles: HomePageArticle[]
      top_regions: TopRegion[]
    }>(`${API_BASE_URL}/homepage/`)

    recentAds.value = response.data.recent_ads || []
    mainArticle.value = response.data.main_article
    sideArticles.value = response.data.side_articles || []
    topRegions.value = response.data.top_regions || []
  } catch (err) {
    const message = axios.isAxiosError(err)
      ? `Не удалось загрузить данные: ${err.message}.`
      : 'Произошла неизвестная ошибка.'
    errorAds.value = message
    errorArticles.value = message
    errorRegions.value = message
  } finally {
    loadingAds.value = false
    loadingArticles.value = false
    loadingRegions.value = false
  }
}

const toggleFavorite = (regionId: number) => {
  // TODO: Реализовать функционал "Избранное"
  console.log(`Toggle favorite for region ID: ${regionId}`)
  alert(`Функционал "Избранное" в разработке!`)
}

onMounted(() => {
  fetchData()
})
</script>
