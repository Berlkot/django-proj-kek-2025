<template>
  <div id="app-container" class="flex flex-col min-h-screen">
    <AppHeader /> <main class="flex-grow">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';
// import { RouterView } from 'vue-router'; // Можно не импортировать, если используется глобально
</script>

<style>
/* Глобальные стили или стили для App.vue */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>