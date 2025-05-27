<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 md:p-10 rounded-xl shadow-lg">
      <div>
        <img class="mx-auto h-12 w-auto" src="/logo.svg" alt="СпасиЗверя">
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Создание аккаунта
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm">
          <div class="mb-3">
            <label for="reg-username" class="sr-only">Имя пользователя (логин)</label>
            <input id="reg-username" v-model="formData.username" name="username" type="text" required
              class="appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Имя пользователя (логин)">
          </div>
          <div class="mb-3">
            <label for="reg-email" class="sr-only">Email</label>
            <input id="reg-email" v-model="formData.email" name="email" type="email" autocomplete="email" required
              class="appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Email">
          </div>
          <div class="mb-3">
            <label for="reg-display_name" class="sr-only">Отображаемое имя</label>
            <input id="reg-display_name" v-model="formData.display_name" name="display_name" type="text"
              class="appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Отображаемое имя (необязательно)">
          </div>
          <div class="mb-3">
            <label for="reg-password" class="sr-only">Пароль</label>
            <input id="reg-password" v-model="formData.password" name="password" type="password"
              autocomplete="new-password" required
              class="appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Пароль">
          </div>
          <div>
            <label for="reg-re_password" class="sr-only">Повторите пароль</label>
            <input id="reg-re_password" v-model="formData.re_password" name="re_password" type="password"
              autocomplete="new-password" required
              class="appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
              placeholder="Повторите пароль">
          </div>
        </div>

        <div v-if="authStore.error && !registrationSuccess" class="bg-red-50 border-l-4 border-red-400 p-3">
          <p class="text-sm text-red-700">{{ authStore.error }}</p>
        </div>

        <div>
          <button type="submit" :disabled="authStore.loading"
            class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50">
            {{ authStore.loading ? 'Обработка...' : 'Зарегистрироваться и войти' }}
          </button>
        </div>
      </form>
      <p class="mt-4 text-center text-sm text-gray-600">
        Уже есть аккаунт?
        <router-link :to="{ name: 'Login' }" class="font-medium text-green-600 hover:text-green-500">
          Войти
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const formData = reactive({
  email: '',
  username: '',
  password: '',
  re_password: '',
  display_name: '',
});
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const registrationSuccess = ref(false);

const handleRegister = async () => {

  authStore.error = null;

  const dataToSend = {
    email: formData.email,
    username: formData.username,
    password: formData.password,
    re_password: formData.re_password,
    display_name: formData.display_name || formData.username,
  };

  const success = await authStore.register(dataToSend);

  if (success) {

    const nextPath = route.query.next as string | undefined;
    router.push(nextPath || { name: 'Home' });
  }


};
</script>
