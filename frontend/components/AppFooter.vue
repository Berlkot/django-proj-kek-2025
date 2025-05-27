<template>
  <footer class="bg-gray-700 text-gray-300 py-10">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        <div>
          <a href="/" class="flex items-center mb-4">

            <img src="/logo.svg" alt="СпасиЗверя" class="h-8 mr-2 filter invert brightness-0">
            <span class="text-xl font-bold text-white">СпасиЗверя</span>
          </a>
          <p class="text-sm">© {{ new Date().getFullYear() }} СПАСИЗВЕРЯ. ВСЕ ПРАВА ЗАЩИЩЕНЫ.</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-3">Навигация</h5>
          <ul class="space-y-2 text-sm">
            <li><router-link :to="{ name: 'Articles' }" class="hover:text-green-400">Статьи</router-link></li>
            <li><a href="/ads" class="hover:text-green-400">Объявления</a></li>
            <li><a href="/privacy" class="hover:text-green-400">Политика конфиденциальности</a></li>
            <li><a href="/sitemap" class="hover:text-green-400">Карта сайта</a></li>
            <li><a href="/rules" class="hover:text-green-400">Правила сервиса</a></li>
          </ul>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-3">Мы в соцсетях</h5>
          <div class="flex space-x-4">
            <a href="#" aria-label="Telegram" class="text-gray-300 hover:text-blue-400">
              <font-awesome-icon :icon="['fab', 'telegram']" size="lg" />
            </a>
            <a href="#" aria-label="VK" class="text-gray-300 hover:text-blue-500">
              <font-awesome-icon :icon="['fab', 'vk']" size="lg" />
            </a>
            <a href="#" aria-label="WhatsApp" class="text-gray-300 hover:text-green-400">
              <font-awesome-icon :icon="['fab', 'whatsapp']" size="lg" />
            </a>
            <a href="#" aria-label="Odnoklassniki" class="text-gray-300 hover:text-orange-400">
              <font-awesome-icon :icon="['fab', 'odnoklassniki']" size="lg" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>
