<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="container mx-auto px-4 py-3 flex justify-between items-center">
      <a href="/" class="flex items-center">
        <img src="/logo.svg" alt="СпасиЗверя" class="h-10 mr-2">
      </a>
      <nav class="hidden md:flex items-center space-x-6 text-gray-700">
        <a href="/articles" class="hover:text-green-600">Статьи</a>
        <a href="/contacts" class="hover:text-green-600">Контакты</a>
        <a href="/ads" class="hover:text-green-600">Объявления</a>
        <a href="/rules" class="hover:text-green-600">Правила сервиса</a>
      </nav>
      <div class="flex items-center space-x-3">
        <button class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100">
          Войти
        </button>
        <button class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600">
          Разместить
        </button>
      </div>
      <!-- Гамбургер меню для мобильных (пока не реализовано) -->
      <div class="md:hidden">
        <button class="text-gray-700 focus:outline-none">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
</script>