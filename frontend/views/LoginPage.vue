<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 md:p-10 rounded-xl shadow-lg">
      <div>
        <img class="mx-auto h-12 w-auto" src="/logo.svg" alt="СпасиЗверя">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Вход в аккаунт
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email-address" class="sr-only">Email</label>
            <input id="email-address" v-model="email" name="email" type="email" autocomplete="email" required
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="Email">
          </div>
          <div>
            <label for="password" class="sr-only">Пароль</label>
            <input id="password" v-model="password" name="password" type="password" autocomplete="current-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10 sm:text-sm"
              placeholder="Пароль">
          </div>
        </div>

        <div v-if="authStore.error" class="bg-red-50 border-l-4 border-red-400 p-3">
          <p class="text-sm text-red-700">{{ authStore.error }}</p>
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
          <button type="submit" :disabled="authStore.loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50">
            <span v-if="authStore.loading" class="absolute left-0 inset-y-0 flex items-center pl-3">

            </span>
            {{ authStore.loading ? 'Вход...' : 'Войти' }}
          </button>
        </div>
      </form>
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

const handleLogin = async () => {
  const success = await authStore.login({ email: email.value, password: password.value });
  if (success) {


    const nextPath = route.query.next as string | undefined;
    router.push(nextPath || { name: 'Home' });
  }
};
</script>
