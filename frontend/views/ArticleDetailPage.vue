<template>
  <div class="bg-gray-50 min-h-screen">
    <div v-if="loading" class="flex justify-center items-center min-h-[calc(100vh-200px)]">
      <p class="text-xl text-gray-500">Загрузка статьи...</p>
    </div>
    <div v-else-if="error" class="container mx-auto px-4 py-10 text-center">
      <p class="text-xl text-red-500 bg-red-100 p-6 rounded-lg shadow">Ошибка: {{ error }}</p>
      <router-link :to="{ name: 'Articles' }" class="mt-6 inline-block bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600">
        Ко всем статьям
      </router-link>
    </div>
    
    <div v-else-if="article" class="article-detail-page">
      <div class="container mx-auto max-w-3xl px-4 pt-8 md:pt-12">
        <!-- ... (Главное изображение, Заголовок, Информация об авторе статьи - уже должно работать с display_name) ... -->
        <div v-if="article.main_image_url" class="mb-6 md:mb-8 rounded-lg overflow-hidden shadow-lg">
          <img :src="article.main_image_url" :alt="article.title" class="w-full h-auto object-cover">
        </div>
        <div v-else-if="!article.main_image_url && !loading" class="mb-6 md:mb-8 h-[200px] bg-gray-200 flex items-center justify-center text-gray-500 rounded-lg">
          Изображение отсутствует
        </div>

        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-800 mb-6 text-center md:text-left">
          {{ article.title }}
        </h1>
        <div class="mb-4" v-if="authStore.isAuthenticated && article && (authStore.user?.is_staff /* || (article.author?.id === authStore.user?.id && authStore.user.role.can_edit_own) || authStore.user.role.can_edit_any */ )">
            <router-link :to="{ name: 'ArticleEdit', params: { id: article.id } }" class="text-sm text-blue-600 hover:text-blue-800 hover:underline">
                <font-awesome-icon :icon="['fas', 'pencil-alt']" class="mr-1"/> Редактировать статью
            </router-link>
        </div>
        <div class="flex items-center mb-8 text-sm text-gray-600">
          <img
            v-if="article.author && article.author.avatar_url"
            :src="article.author.avatar_url"
            :alt="article.author.display_name || 'Аватар автора'"
            class="w-10 h-10 md:w-12 md:h-12 rounded-full mr-3 object-cover"
          >
          <img
            v-else-if="article.author"
            src="/static/images/no-image-data.png"
            alt="Аватар по умолчанию"
            class="w-10 h-10 md:w-12 md:h-12 rounded-full mr-3 object-cover bg-gray-200"
          >
          <div>
            <p v-if="article.author && article.author.display_name" class="font-semibold text-gray-800">
              {{ article.author.display_name }}
            </p>
            <p v-else-if="article.author && article.author.username" class="font-semibold text-gray-800">
              {{ article.author.username }}
            </p>
            <p v-else class="font-semibold text-gray-800">
              Автор неизвестен
            </p>
            <p>{{ formattedPublicationDate }}</p>
          </div>
        </div>
        
        <div
          class="prose prose-sm sm:prose-base lg:prose-lg max-w-none text-gray-700 leading-relaxed article-content"
          v-html="article.content"
        ></div>

        <!-- Блок Комментариев (НОВЫЙ) -->
        <div class="mt-10 mb-10 md:mt-16 pt-8 border-t border-gray-200">
          <h2 class="text-2xl font-semibold text-gray-800 mb-6">
            Комментарии ({{ article.comments ? article.comments.length : 0 }})
          </h2>
          <div v-if="article.comments && article.comments.length > 0" class="space-y-6">
            <div v-for="comment in article.comments" :key="comment.id" class="bg-white p-4 rounded-lg shadow-sm border relative group">
              <div class="flex items-start space-x-4">
                <img 
                  :src="comment.user.avatar_url || '/images/avatar-placeholder.png'" 
                  :alt="comment.user.display_name || 'Аватар комментатора'" 
                  class="w-10 h-10 rounded-full object-cover flex-shrink-0"
                >
                <div class="flex-grow">
                  <p class="font-semibold text-gray-900 text-sm">
                    {{ comment.user.display_name || comment.user.username }} <!-- Имя пользователя -->
                  </p>
                  <p class="text-xs text-gray-500 mb-1.5">{{ formatTimeAgo(comment.date_created) }}</p>
                  
                  <div v-if="editingArticleCommentId === comment.id">
                    <textarea 
                      v-model="editingArticleCommentText" 
                      rows="3" 
                      class="w-full p-2 border rounded-md focus:ring-green-500 focus:border-green-500 text-sm"
                    ></textarea>
                    <div class="mt-2 space-x-2">
                      <button @click="saveEditedArticleComment(comment.id)" :disabled="articleCommentSubmitting" class="text-xs bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded disabled:opacity-50">
                        Сохранить
                      </button>
                      <button @click="cancelEditArticleComment" class="text-xs bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded">
                        Отмена
                      </button>
                    </div>
                    <p v-if="editArticleCommentError" class="text-red-500 text-xs mt-1">{{ editArticleCommentError }}</p>
                  </div>
                  <p v-else class="text-gray-700 text-sm whitespace-pre-line">{{ comment.text }}</p>
                </div>
              </div>
              <!-- Кнопки управления комментарием -->
              <div 
                v-if="authStore.isAuthenticated && (authStore.user?.id === comment.user.id || authStore.user?.is_staff)" 
                class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity flex space-x-1"
              >
                <button 
                  v-if="authStore.user?.id === comment.user.id" 
                  @click="startEditArticleComment(comment)" 
                  title="Редактировать" 
                  class="p-1.5 text-xs text-blue-500 hover:text-blue-700 bg-blue-100 hover:bg-blue-200 rounded"
                  :disabled="editingArticleCommentId !== null && editingArticleCommentId !== comment.id"
                >
                  <font-awesome-icon :icon="['fas', 'pencil-alt']" />
                </button>
                <button 
                  @click="deleteArticleComment(comment.id)" 
                  title="Удалить" 
                  class="p-1.5 text-xs text-red-500 hover:text-red-700 bg-red-100 hover:bg-red-200 rounded"
                  :disabled="editingArticleCommentId !== null && editingArticleCommentId !== comment.id"
                >
                  <font-awesome-icon :icon="['fas', 'trash-alt']" />
                </button>
              </div>
            </div>
          </div>
          <p v-else class="text-gray-600">Комментариев пока нет. Будьте первым!</p>
          
          <!-- Форма добавления комментария -->
          <div class="mt-8 pt-6 border-t border-gray-200">
            <h3 class="text-xl font-semibold text-gray-800 mb-3">Оставить комментарий</h3>
            <div v-if="authStore.isAuthenticated">
              <textarea 
                v-model="newArticleCommentMessage" 
                rows="4" 
                placeholder="Ваш комментарий..." 
                class="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500"
              ></textarea>
              <button 
                @click="submitArticleComment" 
                :disabled="articleCommentSubmitting || !newArticleCommentMessage.trim()" 
                class="mt-3 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-5 rounded-md disabled:opacity-60 transition-colors"
              >
                {{ articleCommentSubmitting ? 'Отправка...' : 'Отправить комментарий' }}
              </button>
              <p v-if="articleCommentError" class="text-red-600 text-sm mt-2">{{ articleCommentError }}</p>
            </div>
            <div v-else>
              <p class="text-gray-700">
                Чтобы оставить комментарий, пожалуйста, 
                <router-link :to="{name: 'Login', query: { next: route.fullPath }}" class="text-green-600 hover:text-green-700 font-semibold hover:underline">войдите</router-link> или 
                <router-link :to="{name: 'Register', query: { next: route.fullPath }}" class="text-green-600 hover:text-green-700 font-semibold hover:underline">зарегистрируйтесь</router-link>.
              </p>
            </div>
          </div>
        </div> <!-- Конец блока комментариев -->
      </div> <!-- Конец контейнера max-w-3xl -->
    </div>
    <div v-else class="flex justify-center items-center min-h-[calc(100vh-200px)]">
       <p class="text-xl text-gray-500">Статья не найдена.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import type { ArticleDetail, Comment as ArticleComment, Author } from '../types'; // Убедимся, что Comment импортирован и переименован, если нужно
import { formatTimeAgo, formatDate } from '../utils/time';
import { useAuthStore } from '../stores/auth';
import { library } from '@fortawesome/fontawesome-svg-core';
import { faPencilAlt, faTrashAlt } from '@fortawesome/free-solid-svg-icons';

library.add(faPencilAlt, faTrashAlt);

const props = defineProps<{
  id: string | number;
}>();

const article = ref<ArticleDetail | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// Для комментариев к статье
const newArticleCommentMessage = ref('');
const articleCommentSubmitting = ref(false);
const articleCommentError = ref<string | null>(null);
const editingArticleCommentId = ref<number | null>(null);
const editingArticleCommentText = ref('');
const editArticleCommentError = ref<string | null>(null);


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const route = useRoute();
const router = useRouter(); // Если нужен для навигации
const authStore = useAuthStore();


const fetchArticleDetail = async (articleId: string | number) => {
  loading.value = true;
  error.value = null;
  article.value = null;
  try {
    // Убедимся, что ArticleDetailSerializer на бэке включает поле 'comments'
    const response = await axios.get<ArticleDetail>(`${API_BASE_URL}/articles/${articleId}/`);
    article.value = response.data;
    if (article.value && !article.value.comments) { // Фоллбэк, если comments не пришел
        article.value.comments = [];
    }
  } catch (err) {
    console.error(`Ошибка при загрузке статьи ${articleId}:`, err);
    if (axios.isAxiosError(err)) {
      error.value = err.response?.status === 404 ? "Статья не найдена." : `Не удалось загрузить статью: ${err.message}.`;
    } else {
      error.value = "Произошла неизвестная ошибка.";
    }
  } finally {
    loading.value = false;
  }
};

const formattedPublicationDate = computed(() => {
  return article.value ? formatDate(article.value.publication_date) : '';
});

// --- Логика CRUD для комментариев к статье ---
const submitArticleComment = async () => {
  if (!newArticleCommentMessage.value.trim() || !article.value || !authStore.isAuthenticated) return;
  articleCommentSubmitting.value = true;
  articleCommentError.value = null;
  try {
    const response = await axios.post<ArticleComment>(
      `${API_BASE_URL}/articles/${article.value.id}/comments/`,
      { text: newArticleCommentMessage.value } // Поле в CommentSerializer - 'text'
    );
    article.value.comments.unshift(response.data);
    newArticleCommentMessage.value = '';
  } catch (err) {
    articleCommentError.value = axios.isAxiosError(err) ? `Ошибка: ${err.response?.data?.detail || err.message}` : "Не удалось отправить комментарий.";
  } finally {
    articleCommentSubmitting.value = false;
  }
};

const startEditArticleComment = (comment: ArticleComment) => {
  editingArticleCommentId.value = comment.id;
  editingArticleCommentText.value = comment.text;
  editArticleCommentError.value = null;
};

const cancelEditArticleComment = () => {
  editingArticleCommentId.value = null;
  editingArticleCommentText.value = '';
  editArticleCommentError.value = null;
};

const saveEditedArticleComment = async (commentId: number) => {
  if (!editingArticleCommentText.value.trim() || !article.value) return;
  articleCommentSubmitting.value = true;
  editArticleCommentError.value = null;
  try {
    const response = await axios.patch<ArticleComment>(
      `${API_BASE_URL}/articles/${article.value.id}/comments/${commentId}/`,
      { text: editingArticleCommentText.value }
    );
    const index = article.value.comments.findIndex(c => c.id === commentId);
    if (index !== -1) {
      article.value.comments[index] = response.data;
    }
    cancelEditArticleComment();
  } catch (err) {
    editArticleCommentError.value = axios.isAxiosError(err) ? `Ошибка: ${err.response?.data?.detail || err.message}` : "Не удалось сохранить изменения.";
  } finally {
    articleCommentSubmitting.value = false;
  }
};

const deleteArticleComment = async (commentId: number) => {
  if (!article.value) return;
  if (!confirm("Вы уверены, что хотите удалить этот комментарий?")) return;
  try {
    await axios.delete(`${API_BASE_URL}/articles/${article.value.id}/comments/${commentId}/`);
    article.value.comments = article.value.comments.filter(c => c.id !== commentId);
  } catch (err) {
    alert(axios.isAxiosError(err) ? `Ошибка: ${err.response?.data?.detail || err.message}` : "Не удалось удалить комментарий.");
  }
};


onMounted(() => {
  fetchArticleDetail(props.id);
});

watch(() => props.id, (newId) => {
  if (newId) {
    fetchArticleDetail(newId);
    cancelEditArticleComment();
  }
});
</script>

<style>
/* Стили для контента, генерируемого v-html */
.article-content h1, .article-content h2, .article-content h3, .article-content h4 {
  @apply font-bold text-gray-800 mb-4 mt-6;
}
.article-content h1 { @apply text-3xl sm:text-4xl; }
.article-content h2 { @apply text-2xl sm:text-3xl; } /* Пример из макета "Как назначают лечение" */
.article-content h3 { @apply text-xl sm:text-2xl; }
.article-content h4 { @apply text-lg sm:text-xl; }

.article-content p {
  @apply mb-4 text-gray-700;
}

.article-content a {
  @apply text-green-600 hover:text-green-700 underline;
}

.article-content ul, .article-content ol {
  @apply list-inside mb-4 pl-4;
}
.article-content ul { @apply list-disc; }
.article-content ol { @apply list-decimal; }

.article-content li {
  @apply mb-2;
}

.article-content blockquote {
  @apply border-l-4 border-gray-300 pl-4 py-2 my-4 italic text-gray-600;
}

.article-content img {
  @apply rounded-lg my-6 shadow-sm max-w-full h-auto mx-auto;
}

.whitespace-pre-line { /* Добавьте, если еще нет */
  white-space: pre-line;
}

</style>