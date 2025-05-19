<template>
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="container mx-auto px-4 py-3 flex justify-between items-center">
      <router-link to="/" class="flex items-center">
        <img src="/logo.svg" alt="СпасиЗверя" class="h-10 mr-2">
      </router-link>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center space-x-4 lg:space-x-6 text-gray-700">
        <router-link to="/ads" class="hover:text-green-600">Объявления</router-link>
        <router-link to="/rules" class="hover:text-green-600">Правила</router-link>
        <router-link to="/contacts" class="hover:text-green-600">Контакты</router-link>
        <router-link :to="{ name: 'Articles' }" class="hover:text-green-600" active-class="text-green-600 font-semibold">Статьи</router-link>
      </nav>

      <!-- Desktop Action Buttons -->
      <div class="hidden md:flex items-center space-x-3">
        <button @click="navigateTo('/login')" class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100">
          Войти
        </button>
        <button @click="navigateTo('/post-ad')" class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600">
          Разместить
        </button>
      </div>

      <!-- Mobile Menu Button -->
      <div class="md:hidden">
        <button @click="toggleMobileMenu" class="text-gray-700 focus:outline-none">
          <font-awesome-icon :icon="['fas', 'bars']" class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- Mobile Menu Panel -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 -translate-y-10"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 -translate-y-10"
    >
      <div v-if="isMobileMenuOpen" class="md:hidden absolute top-full left-0 right-0 bg-white shadow-lg z-40">
        <nav class="flex flex-col px-4 pt-2 pb-4 space-y-1 border-t border-gray-200">
          <router-link @click="closeMobileMenu" to="/ads" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600">Объявления</router-link>
          <router-link @click="closeMobileMenu" to="/rules" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600">Правила</router-link>
          <router-link @click="closeMobileMenu" to="/contacts" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600">Контакты</router-link>
          <router-link @click="closeMobileMenu" :to="{ name: 'Articles' }" class="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100 hover:text-green-600" active-class="bg-gray-100 text-green-600">Статьи</router-link>
          <hr class="my-2">
          <button @click="handleMobileAuthClick('/login')" class="w-full text-left block px-3 py-2 border border-gray-300 rounded-md text-base font-medium text-gray-700 hover:bg-gray-100">
            Войти
          </button>
          <button @click="handleMobileAuthClick('/register')" class="w-full text-left block mt-2 px-3 py-2 bg-green-500 text-white rounded-md text-base font-medium hover:bg-green-600">
            Регистрация
          </button>
        </nav>
      </div>
    </transition>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // Import if you use vue-router

const router = useRouter(); // Initialize router if used

const isMobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

// For navigation from buttons, if you use vue-router
const navigateTo = (path: string) => {
  router.push(path);
};

const handleMobileAuthClick = (path: string) => {
  closeMobileMenu();
  navigateTo(path);
};

// Close mobile menu if clicked outside - optional, can be complex
// onMounted(() => {
//   const handleClickOutside = (event: MouseEvent) => {
//     const menuElement = document.querySelector('.mobile-menu-panel-class'); // Add a class to your panel
//     const buttonElement = document.querySelector('.mobile-menu-button-class'); // Add a class to your button
//     if (
//       menuElement &&
//       !menuElement.contains(event.target as Node) &&
//       buttonElement &&
//       !buttonElement.contains(event.target as Node)
//     ) {
//       closeMobileMenu();
//     }
//   };
//   if (isMobileMenuOpen.value) { // Only add listener if menu can be open
//      document.addEventListener('click', handleClickOutside, true);
//   }
// });
// onUnmounted(() => {
//   document.removeEventListener('click', handleClickOutside, true);
// });
</script>