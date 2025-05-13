<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 flex">
    <img :src="imageUrl" :alt="title" class="w-1/3 h-auto object-cover">
    <div class="p-4 w-2/3">
      <h4 class="text-md font-semibold text-gray-800 mb-1">{{ title }}</h4>
      <p class="text-xs text-gray-600 mb-2 h-10 overflow-hidden text-ellipsis">{{ description }}</p>
      <span class="text-xs text-gray-500">{{ timeAgo }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  imageUrl: string;
  title: string;
  description: string;
  timeAgo: string;
}>();
</script>