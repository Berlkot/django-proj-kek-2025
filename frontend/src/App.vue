<template>
  <div class="flex flex-col min-h-screen bg-gray-50">
    <AppHeader />
    <main class="flex-grow">
      <!-- Если используете Vue Router, здесь будет <router-view /> -->
      <HomePage /> <!-- Для примера直接 вставляем HomePage -->
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
import HomePage from './views/HomePage.vue'; // Компонент главной страницы
</script>