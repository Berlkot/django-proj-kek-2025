<template>

  <router-link :to="adLink"
    class="group block bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 flex flex-col h-full">
    <div class="relative overflow-hidden rounded-t-lg">
      <img :src="imageUrl" :alt="title"
        class="w-full h-48 object-cover group-hover:opacity-80 transition-opacity duration-300" />

      <span v-if="adType" class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded">
        {{ adType }}
      </span>
    </div>
    <div class="p-4 flex flex-col flex-grow">
      <h3 class="text-lg font-semibold text-gray-800 mb-1 truncate group-hover:text-green-600 transition-colors">
        {{ title }}
      </h3>

      <p v-if="speciesName" class="text-xs text-gray-500 mb-1">{{ speciesName }}</p>
      <p class="text-sm text-gray-600 mb-3 flex-grow h-16 overflow-hidden text-ellipsis line-clamp-3">
        {{ description }}
      </p>
      <div class="flex justify-between items-center text-xs text-gray-500 mt-auto pt-2 border-t border-gray-100">
        <span class="flex items-center truncate" :title="location">
          <font-awesome-icon :icon="['fas', 'map-marker-alt']" class="mr-1 flex-shrink-0" />
          <span class="truncate">{{ location || 'Не указано' }}</span>
        </span>
        <span>{{ timeAgo }}</span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  id: number;
  imageUrl: string;
  title: string;
  description: string;
  location: string;
  timeAgo: string;
  adType?: string;
  speciesName?: string;
}>();

const adLink = computed(() => `/advertisement/${props.id}`);
</script>

<style scoped>
.line-clamp-3 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
</style>
