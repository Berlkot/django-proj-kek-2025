<template>
  <!-- 1. Вся карточка теперь ссылка -->
  <router-link
    :to="articleLink"
    class="group bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-col h-full"
  >
    <!-- Убрал router-link с картинки, так как родитель теперь ссылка -->
    <div class="relative overflow-hidden rounded-t-lg"> <!-- Обертка для картинки -->
      <img
        :src="article.main_image_url || '/images/no-image-data.png'"
        :alt="article.title"
        class="w-full object-cover transition-opacity duration-300"
        :class="[
          large ? 'h-64 sm:h-72 md:h-80 lg:h-96' : 'h-48',
          'group-hover:opacity-80' /* 2. Ховер-эффект на картинку */
        ]"
      />
    </div>
    <!-- 3. Текстовый блок большой карточки будет растягиваться -->
    <div
      class="p-4 md:p-5 flex flex-col"
      :class="{ 'flex-grow': large }"
    >
      <!-- Убрал router-link с заголовка -->
      <h3
        class="font-semibold text-gray-800 group-hover:text-green-600 transition-colors line-clamp-2"
        :class="[
          large ? 'text-xl md:text-2xl' : 'text-lg',
          large ? 'min-h-[calc(theme(fontSize.xl[1].lineHeight)_*_2)] md:min-h-[calc(theme(fontSize.2xl[1].lineHeight)_*_2)]' : 'min-h-[3rem]'
        ]"
      >
        {{ article.title }}
      </h3>
      <p
        class="text-gray-600 mb-3 line-clamp-3"
        :class="[
          large ? 'text-base flex-grow' : 'text-sm', // Добавил flex-grow для описания большой карточки
          large ? 'min-h-[calc(theme(fontSize.base[1].lineHeight)_*_3)]' : 'min-h-[3.75rem]'
        ]"
      >
        {{ article.excerpt }}
      </p>
      <div class="text-xs text-gray-500 mt-auto pt-3 border-t border-gray-100">
        <span>{{ formattedTimeAgo }}</span>
        <span v-if="article.categories && article.categories.length" class="ml-2 hidden sm:inline">
          | {{ article.categories.map(c => c.name).join(', ') }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatTimeAgo } from '../utils/time';

interface ArticleCategory {
  id: number;
  name: string;
  slug: string;
}

interface ArticleForCard {
  id: number;
  title: string;
  excerpt: string;
  publication_date: string;
  main_image_url: string | null;
  categories?: ArticleCategory[];
}

const props = withDefaults(defineProps<{
  article: ArticleForCard;
  large?: boolean;
}>(), {
  large: false,
});

const articleLink = computed(() => ({ name: 'ArticleDetail', params: { id: props.article.id }}));
const formattedTimeAgo = computed(() => formatTimeAgo(props.article.publication_date));
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}
.line-clamp-3 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
</style>