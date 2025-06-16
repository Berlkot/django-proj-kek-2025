<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 md:p-10 rounded-xl shadow-lg">
      <div>
        <img class="mx-auto h-12 w-auto" src="/static/logo.svg" alt="СпасиЗверя">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Вход в аккаунт
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div v-if="generalError" class="bg-red-50 border-l-4 border-red-400 p-3">
            <p class="text-sm text-red-700">{{ generalError }}</p>
        </div>
        
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email-address" class="sr-only">Email</label>
            <input
              id="email-address"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="Email"
            >
            <p v-if="formErrors.email" class="text-red-500 text-xs mt-1 px-1">{{ formErrors.email.join(', ') }}</p>
          </div>
          <div>
            <label for="password" class="sr-only">Пароль</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="Пароль"
            >
            <p v-if="formErrors.password" class="text-red-500 text-xs mt-1 px-1">{{ formErrors.password.join(', ') }}</p>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input id="remember-me" name="remember-me" type="checkbox"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded">
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              Запомнить меня
            </label>
          </div>
          <div class="text-sm">
            <a href="#" class="font-medium text-green-600 hover:text-green-500">
              Забыли пароль?
            </a>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="authStore.loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ authStore.loading ? 'Вход...' : 'Войти' }}
          </button>
        </div>
      </form>
      <div class="relative my-4">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">Или войдите через</span>
        </div>
      </div>
      
      <div class="space-y-3">
        <button @click="redirectToProvider('google-oauth2')" class="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
          <font-awesome-icon :icon="['fab', 'google']" class="h-5 w-5 mr-2"/>
          Войти через Google
        </button>
        <!-- пошёл нахер vk -->
        <!-- <button @click="redirectToProvider('vk-oauth2')" class="w-full flex items-center justify-center py-2 px-4 border border-blue-600 rounded-md shadow-sm bg-blue-600 text-sm font-medium text-white hover:bg-blue-700">
          <font-awesome-icon :icon="['fab', 'vk']" class="mr-2 text-lg" />
          Войти через ВКонтакте
          </button> -->
      </div>

      <p class="mt-4 text-center text-sm text-gray-600">
        Нет аккаунта?
        <router-link :to="{ name: 'Register' }" class="font-medium text-green-600 hover:text-green-500">
          Зарегистрироваться
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const email = ref('');
const password = ref('');
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();

// Локальное состояние для ошибок полей и общих ошибок
const formErrors = ref<Record<string, string[]>>({}); 
const generalError = ref<string | null>(null);
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const redirectToProvider = (provider: 'google-oauth2' | 'vk-oauth2') => {
     window.location.href = `${API_BASE_URL}/social/login/${provider}/`;
}

const handleLogin = async () => {
  formErrors.value = {}; // Сброс ошибок полей
  generalError.value = null; // Сброс общих ошибок
  authStore.error = null; // Сброс общей ошибки в сторе

  const result = await authStore.login({ email: email.value, password: password.value });

  if (result.success) {
    const nextPath = route.query.next as string | undefined;
    router.push(nextPath || { name: 'Home' });
  } else {
    if (result.errors) {
      // Djoser для эндпоинта /jwt/create/ обычно возвращает ошибки в поле "detail" или "non_field_errors"
      // но на всякий случай обрабатываем как объект
      if (typeof result.errors === 'object' && result.errors !== null) {
        if (result.errors.detail) {
          generalError.value = String(result.errors.detail);
        } else if (result.errors.non_field_errors && Array.isArray(result.errors.non_field_errors)) {
          generalError.value = result.errors.non_field_errors.join('; ');
        } else {
          // Если есть ошибки по конкретным полям (маловероятно для стандартного JWT create, но возможно для кастомного)
          formErrors.value = result.errors as Record<string, string[]>;
          // Попробуем сформировать общее сообщение, если есть ошибки по полям, но нет non_field_errors
          const fieldErrorMessages = Object.values(formErrors.value).flat();
          if (fieldErrorMessages.length > 0) {
            generalError.value = fieldErrorMessages.join('; ');
          } else {
            generalError.value = "Произошла ошибка входа.";
          }
        }
      } else if (typeof result.errors === 'string') {
        generalError.value = result.errors;
      }
    } else if (authStore.error) {
      generalError.value = authStore.error;
    }
    if (!generalError.value && Object.keys(formErrors.value).length === 0) {
        generalError.value = "Ошибка входа. Проверьте email и пароль.";
    }
  }
};
</script>
