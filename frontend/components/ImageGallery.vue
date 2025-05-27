<template>
  <div v-if="photos && photos.length > 0" class="image-gallery">
    <div class="main-image-container mb-3 relative">
      <img :src="currentPhotoUrl" :alt="`Фото объявления ${currentIndex + 1}`"
        class="w-full max-h-[400px] md:max-h-[500px] object-contain rounded-lg shadow-md bg-gray-100" />
      <button v-if="photos.length > 1" @click="prevPhoto"
        class="absolute left-2 top-1/2 -translate-y-1/2 bg-black bg-opacity-40 hover:bg-opacity-60 text-white p-2 rounded-full transition-opacity z-10"
        aria-label="Предыдущее фото">
        <font-awesome-icon :icon="['fas', 'chevron-left']" class="w-5 h-5" />
      </button>
      <button v-if="photos.length > 1" @click="nextPhoto"
        class="absolute right-2 top-1/2 -translate-y-1/2 bg-black bg-opacity-40 hover:bg-opacity-60 text-white p-2 rounded-full transition-opacity z-10"
        aria-label="Следующее фото">
        <font-awesome-icon :icon="['fas', 'chevron-right']" class="w-5 h-5" />
      </button>

      <div v-if="photos.length > 1 && photos.length <= 7"
        class="absolute bottom-3 left-1/2 -translate-x-1/2 flex space-x-2">
        <button v-for="(photo, index) in photos" :key="photo.id" @click="currentIndex = index"
          :class="['w-3 h-3 rounded-full', currentIndex === index ? 'bg-white' : 'bg-gray-400 hover:bg-gray-200 opacity-75']"
          :aria-label="`Фото ${index + 1}`"></button>
      </div>
    </div>
    <div v-if="photos.length > 1"
      class="thumbnails-container grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2">
      <img v-for="(photo, index) in photos" :key="photo.id" :src="photo.image_url" :alt="`Миниатюра ${index + 1}`"
        @click="currentIndex = index"
        class="w-full h-20 md:h-24 object-cover rounded-md cursor-pointer border-2 transition-all"
        :class="currentIndex === index ? 'border-green-500 opacity-100 scale-105' : 'border-transparent opacity-70 hover:opacity-100'" />
    </div>
  </div>
  <div v-else class="w-full h-[300px] bg-gray-200 flex items-center justify-center rounded-lg text-gray-500">
    Нет фото
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { AdPhoto } from '../types';

const props = defineProps<{
  photos: AdPhoto[];
}>();

const currentIndex = ref(0);

const currentPhotoUrl = computed(() => {
  return props.photos && props.photos.length > 0 ? props.photos[currentIndex.value]?.image_url : '/images/no-image-data.png';
});

const nextPhoto = () => {
  if (props.photos && props.photos.length > 0) {
    currentIndex.value = (currentIndex.value + 1) % props.photos.length;
  }
};

const prevPhoto = () => {
  if (props.photos && props.photos.length > 0) {
    currentIndex.value = (currentIndex.value - 1 + props.photos.length) % props.photos.length;
  }
};

watch(() => props.photos, () => {
  currentIndex.value = 0;
}, { deep: true });
</script>
