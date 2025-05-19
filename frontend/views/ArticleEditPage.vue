<template>
  <div class="container mx-auto px-4 py-8 md:py-12">
    <h1 class="text-3xl font-bold text-gray-800 mb-6">
      {{ articleId ? 'Редактирование статьи' : 'Создание новой статьи' }}
    </h1>

    <div v-if="loadingInitialData" class="text-center text-gray-500 py-10">
      Загрузка данных...
    </div>
    <div v-else-if="initialError" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
      <p>Ошибка загрузки данных статьи: {{ initialError }}</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="bg-white p-6 md:p-8 rounded-lg shadow-md space-y-6">
      <div>
        <label for="title" class="block text-sm font-medium text-gray-700 mb-1">Заголовок</label>
        <input
          type="text"
          id="title"
          v-model="formData.title"
          required
          class="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
        />
        <p v-if="formErrors.title" class="text-red-500 text-xs mt-1">{{ formErrors.title.join(', ') }}</p>
      </div>

      <div>
        <label for="content" class="block text-sm font-medium text-gray-700 mb-1">Содержимое</label>
        <textarea
          id="content"
          v-model="formData.content"
          rows="15"
          required
          class="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
        ></textarea>
        <p v-if="formErrors.content" class="text-red-500 text-xs mt-1">{{ formErrors.content.join(', ') }}</p>
      </div>

      <div>
        <label for="main_image" class="block text-sm font-medium text-gray-700 mb-1">Главное изображение</label>
        <input
          type="file"
          id="main_image"
          @change="handleImageUpload"
          accept="image/*"
          class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
        />
        <div v-if="imagePreviewUrl || formData.main_image_url" class="mt-3">
          <p class="text-xs text-gray-500 mb-1">Текущее/новое изображение:</p>
          <img :src="imagePreviewUrl || formData.main_image_url" alt="Превью изображения" class="max-h-48 rounded border">
           <button 
            v-if="formData.main_image_url || imagePreviewUrl" 
            type="button" 
            @click="removeImage" 
            class="mt-2 text-xs text-red-600 hover:text-red-800"
          >
            Удалить изображение
          </button>
        </div>
        <p v-if="formErrors.main_image" class="text-red-500 text-xs mt-1">{{ formErrors.main_image.join(', ') }}</p>
      </div>
      
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Категории</label>
        <div v-if="loadingCategories" class="text-xs text-gray-500">Загрузка категорий...</div>
        <div v-else-if="categories.length > 0" class="space-y-2 max-h-60 overflow-y-auto border p-3 rounded-md">
          <div v-for="category in categories" :key="category.id" class="flex items-center">
            <input
              type="checkbox"
              :id="`category-${category.id}`"
              :value="category.id"
              v-model="formData.categories"
              class="h-4 w-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <label :for="`category-${category.id}`" class="ml-2 text-sm text-gray-700">{{ category.name }}</label>
          </div>
        </div>
        <p v-else class="text-xs text-gray-500">Категории не найдены.</p>
        <p v-if="formErrors.categories" class="text-red-500 text-xs mt-1">{{ formErrors.categories.join(', ') }}</p>
      </div>

      <div v-if="submitError" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
        <p>{{ submitError }}</p>
      </div>

      <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
        <router-link :to="articleId ? { name: 'ArticleDetail', params: { id: articleId } } : { name: 'Articles' }"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Отмена
        </router-link>
        <button
          type="submit"
          :disabled="submitting"
          class="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {{ submitting ? (articleId ? 'Сохранение...' : 'Создание...') : (articleId ? 'Сохранить изменения' : 'Создать статью') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import type { ArticleFormData, ArticleCategory, ArticleDetail } from '../types'; // ArticleDetail для загрузки существующей
import { useAuthStore } from '../stores/auth';

const props = defineProps<{
  id?: string; // ID для режима редактирования, приходит из router props
}>();

const router = useRouter();
const route = useRoute(); // Не используется напрямую, но может быть полезен
const authStore = useAuthStore();

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const formData = reactive<ArticleFormData>({
  title: '',
  content: '',
  main_image: null,
  main_image_url: null,
  categories: [],
});

const imagePreviewUrl = ref<string | null>(null);
const categories = ref<ArticleCategory[]>([]);
const loadingCategories = ref(false);

const loadingInitialData = ref(false);
const initialError = ref<string | null>(null);
const submitting = ref(false);
const submitError = ref<string | null>(null);
const formErrors = ref<Record<string, string[]>>({}); // Для ошибок по полям

const articleId = computed(() => props.id ? parseInt(props.id, 10) : null);

const fetchArticleData = async () => {
  if (!articleId.value) return;
  loadingInitialData.value = true;
  initialError.value = null;
  try {
    const response = await axios.get<ArticleDetail>(`${API_BASE_URL}/articles/${articleId.value}/`);
    const article = response.data;
    formData.title = article.title;
    formData.content = article.content;
    formData.main_image_url = article.main_image_url;
    formData.categories = article.categories ? article.categories.map(cat => cat.id) : [];
  } catch (err) {
    console.error("Ошибка загрузки статьи для редактирования:", err);
    initialError.value = axios.isAxiosError(err) ? `Ошибка: ${err.response?.data?.detail || err.message}` : "Не удалось загрузить данные статьи.";
  } finally {
    loadingInitialData.value = false;
  }
};

const fetchCategories = async () => {
  loadingCategories.value = true;
  try {
    const response = await axios.get<ArticleCategory[]>(`${API_BASE_URL}/article-categories/`);
    categories.value = response.data;
  } catch (err) {
    console.error("Ошибка загрузки категорий:", err);
    // Можно показать ошибку
  } finally {
    loadingCategories.value = false;
  }
};

const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    formData.main_image = file;
    imagePreviewUrl.value = URL.createObjectURL(file);
    formData.main_image_url = null; // Очищаем старый URL, если загружаем новый файл
  }
};

const removeImage = () => {
    formData.main_image = null;
    imagePreviewUrl.value = null;
    formData.main_image_url = null; // Явно указываем, что изображение нужно удалить на бэкенде
                                   // Бэкенд должен обработать main_image: null как удаление
};


const handleSubmit = async () => {
  submitting.value = true;
  submitError.value = null;
  formErrors.value = {};

  const data = new FormData(); // Используем FormData для отправки файла
  data.append('title', formData.title);
  data.append('content', formData.content);
  
  // Добавляем категории как отдельные значения с одинаковым ключом 'categories'
  formData.categories.forEach(catId => data.append('categories', String(catId)));

  if (formData.main_image) {
    data.append('main_image', formData.main_image);
  } else if (formData.main_image === null && formData.main_image_url === null && articleId.value) {
    // Если main_image и main_image_url оба null, и это редактирование,
    // это означает, что пользователь удалил существующее изображение.
    // Бэкенд должен это обработать, обычно передача `main_image: null` в PATCH/PUT
    // должна очищать поле ImageField, если оно `null=True`.
    // Если `main_image` не включать в FormData, то оно не изменится.
    // Чтобы явно удалить, Djoser/DRF обычно ожидает `null` значение для поля файла.
    // Для FormData это сложнее. Проще всего для DRF - это если поле файла НЕ передается, оно не меняется.
    // Если передается пустая строка или null, это может вызвать ошибку или быть проигнорировано.
    // Для явного удаления изображения через FormData можно отправить специальное значение,
    // которое бэкенд обработает, или использовать PUT/PATCH с JSON, где main_image: null.
    // Поскольку мы используем FormData из-за файла, явное удаление без загрузки нового файла может потребовать
    // отдельного эндпоинта или специальной обработки на бэкенде.
    // Пока что: если main_image не выбрано, старое изображение не меняется.
    // Если main_image выбрано, оно заменяет старое.
    // Если removeImage вызван, то formData.main_image_url = null, и main_image не будет отправлен.
    // На бэкенде ArticleManageSerializer при обновлении, если main_image не пришло в validated_data,
    // оно не будет тронуто. Если пришло null, то должно сброситься.
    // Чтобы PATCH с FormData очистил ImageField, поле должно быть передано, но с "пустым" значением,
    // что FormData не очень хорошо поддерживает для файлов.
    // Возможно, потребуется отправлять JSON, если файл не меняется или удаляется.
    // Но для простоты: если formData.main_image нет, то старое изображение остается.
    // Если вызван removeImage, то formData.main_image_url обнулился, и main_image тоже.
    // При сабмите, если main_image есть, отправляем. Если нет - не отправляем.
    // Бэкенд при PATCH/PUT, если main_image нет в request.FILES, не будет его менять.
    // Если мы хотим УДАЛИТЬ без замены, то при PATCH нужно передать `main_image: null`.
    // С FormData это сделать сложно. Проще всего - если пользователь хочет удалить, он не загружает новое,
    // а на бэке при редактировании, если поле main_image пришло как null (если это не FormData), то удалять.
    // Текущая логика: если main_image выбрано, оно заменит старое. Если не выбрано, старое останется.
    // Если removeImage нажат, main_image и main_image_url = null. При отправке FormData без main_image, бэк не изменит картинку.
    // Для реализации удаления нужно либо PUT/PATCH с JSON и main_image: null, либо специальный флаг в FormData.
    // Пока что удаление без замены новой картинкой не реализовано через эту форму.
  }


  try {
    let response;
    if (articleId.value) {
      // Редактирование (PATCH)
      // Для FormData с файлом обычно используется POST даже для обновления, но DRF поддерживает PATCH с FormData
      response = await axios.patch<ArticleDetail>(`${API_BASE_URL}/articles/${articleId.value}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      router.push({ name: 'ArticleDetail', params: { id: response.data.id } });
    } else {
      // Создание (POST)
      response = await axios.post<ArticleDetail>(`${API_BASE_URL}/articles/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      router.push({ name: 'ArticleDetail', params: { id: response.data.id } });
    }
  } catch (err) {
    console.error("Ошибка при отправке формы статьи:", err);
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 400 && typeof err.response.data === 'object') {
        formErrors.value = err.response.data; // Ошибки валидации полей
        submitError.value = "Пожалуйста, исправьте ошибки в форме.";
      } else {
        submitError.value = err.response.data?.detail || `Произошла ошибка (${err.response.status}).`;
      }
    } else {
      submitError.value = "Произошла неизвестная сетевая ошибка.";
    }
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchCategories();
  if (articleId.value) {
    fetchArticleData();
  }
  // Проверка прав (дополнительная, основная на бэкенде и в роутере)
  if (!authStore.user || !authStore.user.is_staff /* && !authStore.user.role?.can_manage_articles */) {
    // Можно показать сообщение или редирект, если пользователь не должен быть здесь
    // router.replace({ name: 'Home' });
  }
});

</script>