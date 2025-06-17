<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="text-center p-6">
      <h1 class="text-2xl font-semibold text-gray-700 mb-2">Завершение входа...</h1>
      <p v-if="error" class="text-red-500">{{ error }}</p>
      <p v-else class="text-gray-500">Пожалуйста, подождите.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const accessToken = route.query.access as string | null
    const refreshToken = route.query.refresh as string | null

    if (!accessToken || !refreshToken) {
      throw new Error('Один или несколько токенов аутентификации отсутствуют.')
    }

    authStore.setTokens(accessToken, refreshToken)

    await authStore.fetchUser()

    router.replace({ name: 'Home' })
  } catch (e: any) {
    console.error('Social auth callback error:', e)
    error.value = e.message || 'Произошла неизвестная ошибка.'
    authStore.clearAuthData()
  }
})
</script>
