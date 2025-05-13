<template>
  <footer class="bg-gray-700 text-gray-300 py-10">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        <div>
          <a href="/" class="flex items-center mb-4">
            <img src="/logo.svg" alt="СпасиЗверя" class="h-8 mr-2 filter invert brightness-0">
            <span class="text-xl font-bold text-white">СпасиЗверя</span>
          </a>
          <p class="text-sm">© 2024 СПАСИЗВЕРЯ. ВСЕ ПРАВА ЗАЩИЩЕНЫ.</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-3">Навигация</h5>
          <ul class="space-y-2 text-sm">
            <li><a href="/articles" class="hover:text-green-400">Статьи</a></li>
            <li><a href="/ads" class="hover:text-green-400">Объявления</a></li>
            <li><a href="/privacy" class="hover:text-green-400">Политика конфиденциальности</a></li>
            <li><a href="/sitemap" class="hover:text-green-400">Карта сайта</a></li>
            <li><a href="/rules" class="hover:text-green-400">Правила сервиса</a></li>
          </ul>
        </div>
        <div>
          <h5 class="flex font-semibold text-white mb-3">Мы в соцсетях</h5>
          <div class="flex space-x-4">
            <!-- Замените # на реальные ссылки и используйте иконки SVG или FontAwesome -->
            <a href="#" class="bg-blue-500 p-2 rounded-full text-white hover:bg-blue-600">Tlg</a>
            <a href="#" class="bg-blue-700 p-2 rounded-full text-white hover:bg-blue-800">VK</a>
            <a href="#" class="bg-green-500 p-2 rounded-full text-white hover:bg-green-600">WA</a>
            <a href="#" class="bg-orange-500 p-2 rounded-full text-white hover:bg-orange-600">OK</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
// Логика футера, если нужна
</script>