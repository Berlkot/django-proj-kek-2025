<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300">
    <img :src="imageUrl" :alt="title" class="w-full h-48 object-cover">
    <div class="p-4">
      <h3 class="text-lg font-semibold text-gray-800 mb-1 truncate">{{ title }}</h3>
      <p class="text-sm text-gray-600 mb-3 h-16 overflow-hidden text-ellipsis">{{ description }}</p>
      <div class="flex justify-between items-center text-xs text-gray-500">
        <span>📍 {{ location }}</span>
        <span>{{ timeAgo }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  imageUrl: string;
  title: string;
  description: string;
  location: string;
  timeAgo: string;
}>();
</script>