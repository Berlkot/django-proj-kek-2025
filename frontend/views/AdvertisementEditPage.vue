<template>
  <div class="container mx-auto px-4 py-8 md:py-12">
    <div class="flex justify-between items-center mb-6">
          <h1 class="text-3xl font-bold text-gray-800">
            {{ adId ? 'Редактирование объявления' : 'Создание нового объявления' }}
          </h1>
          <!-- Кнопка удаления, если это редактирование и есть права -->
          <button
            v-if="adId && canDeleteCurrentAd"
            @click="handleDeleteAd"
            :disabled="deletingAd"
            type="button"
            class="px-4 py-2 border border-red-500 rounded-md text-sm font-medium text-red-500 hover:bg-red-50 disabled:opacity-50"
          >
            <font-awesome-icon :icon="['fas', 'trash-alt']" class="mr-2"/>
            {{ deletingAd ? 'Удаление...' : 'Удалить объявление' }}
          </button>
        </div>

    <div v-if="loadingInitialData" class="text-center text-gray-500 py-10">Загрузка...</div>
    <div v-else-if="initialError" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
      <p>Ошибка загрузки: {{ initialError }}</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="bg-white p-6 md:p-8 rounded-lg shadow-md space-y-6">
      <!-- Данные объявления -->
      <fieldset class="border p-4 rounded-md">
        <legend class="text-lg font-semibold px-2 text-gray-700">Объявление</legend>
        <div>
          <label for="ad-title" class="block text-sm font-medium text-gray-700 mb-1">Заголовок*</label>
          <input type="text" id="ad-title" v-model="formData.title" required class="w-full input-field" />
          <p v-if="formErrors.title" class="error-text">{{ formErrors.title.join(', ') }}</p>
        </div>
        <div class="mt-4">
          <label for="ad-description" class="block text-sm font-medium text-gray-700 mb-1">Описание*</label>
          <textarea id="ad-description" v-model="formData.description" rows="5" required class="w-full input-field"></textarea>
          <p v-if="formErrors.description" class="error-text">{{ formErrors.description.join(', ') }}</p>
        </div>
        <div class="mt-4">
          <label for="ad-status" class="block text-sm font-medium text-gray-700 mb-1">Тип объявления*</label>
          <select id="ad-status" v-model="formData.status" required class="w-full input-field">
            <option :value="null" disabled>Выберите тип</option>
            <option v-for="st in availableStatusesForCreate" :key="st.id" :value="st.id">{{ st.name }}</option>
          </select>
          <p v-if="formErrors.status" class="error-text">{{ formErrors.status.join(', ') }}</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label for="ad-latitude" class="block text-sm font-medium text-gray-700 mb-1">Широта (необязательно)</label>
            <input type="number" step="any" id="ad-latitude" v-model.number="formData.latitude" class="w-full input-field" />
          </div>
          <div>
            <label for="ad-longitude" class="block text-sm font-medium text-gray-700 mb-1">Долгота (необязательно)</label>
            <input type="number" step="any" id="ad-longitude" v-model.number="formData.longitude" class="w-full input-field" />
          </div>
        </div>
      </fieldset>

      <!-- Данные животного -->
      <fieldset class="border p-4 rounded-md mt-6">
        <legend class="text-lg font-semibold px-2 text-gray-700">Животное</legend>
        <div>
          <label for="animal-name" class="block text-sm font-medium text-gray-700 mb-1">Кличка (необязательно)</label>
          <input type="text" id="animal-name" v-model="formData.animal_data.name" class="w-full input-field" />
        </div>
        <div class="mt-4">
          <label for="animal-birthdate" class="block text-sm font-medium text-gray-700 mb-1">Дата рождения (прим.)</label>
          <input type="date" id="animal-birthdate" v-model="formData.animal_data.birth_date" class="w-full input-field" />
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label for="animal-species" class="block text-sm font-medium text-gray-700 mb-1">Вид*</label>
            <select id="animal-species" v-model="formData.animal_data.species" @change="selectedSpeciesChanged" required class="w-full input-field">
              <option :value="null" disabled>Выберите вид</option>
              <option v-for="s in filterOptions.species" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
            <p v-if="formErrors.animal_data?.species" class="error-text">{{ formErrors.animal_data.species.join(', ') }}</p>
          </div>
          <div>
            <label for="animal-breed" class="block text-sm font-medium text-gray-700 mb-1">Порода (необязательно)</label>
            <select id="animal-breed" v-model="formData.animal_data.breed" :disabled="!formData.animal_data.species || availableBreeds.length === 0" class="w-full input-field">
              <option :value="null">Выберите породу</option>
              <option v-for="b in availableBreeds" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
          </div>
        </div>
         <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label for="animal-color" class="block text-sm font-medium text-gray-700 mb-1">Окрас (необязательно)</label>
            <select id="animal-color" v-model="formData.animal_data.color" class="w-full input-field">
              <option :value="null">Выберите окрас</option>
              <option v-for="c in filterOptions.colors" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label for="animal-gender" class="block text-sm font-medium text-gray-700 mb-1">Пол (необязательно)</label>
            <select id="animal-gender" v-model="formData.animal_data.gender" class="w-full input-field">
              <option :value="null">Выберите пол</option>
              <option v-for="g in filterOptions.genders" :key="g.value" :value="g.value">{{ g.label }}</option>
            </select>
          </div>
        </div>
      </fieldset>

      <!-- Фотографии -->
      <fieldset class="border p-4 rounded-md mt-6">
        <legend class="text-lg font-semibold px-2 text-gray-700">Фотографии</legend>
        <input
          type="file"
          id="photos-upload"
          multiple
          @change="handlePhotoUpload"
          accept="image/*"
          class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
        />
        <div class="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          <!-- Превью новых фото -->
          <div v-for="(file, index) in newPhotoPreviews" :key="`new-${index}`" class="relative">
            <img :src="file.url" :alt="`Превью ${file.name}`" class="w-full h-32 object-cover rounded-md border">
            <button type="button" @click="removeNewPhoto(index)" class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 w-5 h-5 flex items-center justify-center text-xs">×</button>
          </div>
          <!-- Существующие фото (при редактировании) -->
          <div v-for="photo in existingPhotos" :key="`existing-${photo.id}`" class="relative">
            <img :src="photo.image_url" :alt="`Фото ${photo.id}`" class="w-full h-32 object-cover rounded-md border">
            <button type="button" @click="removeExistingPhoto(photo.id)" class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-0.5 w-5 h-5 flex items-center justify-center text-xs">×</button>
          </div>
        </div>
        <p v-if="formErrors.photos_upload" class="error-text">{{ formErrors.photos_upload.join(', ') }}</p>
      </fieldset>
      

      <div v-if="submitError" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
        <p>{{ submitError }}</p>
      </div>

      <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
        <router-link :to="adId ? { name: 'AdvertisementDetail', params: { id: adId } } : { name: 'Advertisements' }"
          class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Отмена
        </router-link>
        <button
          type="submit"
          :disabled="submitting"
          class="px-6 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 disabled:opacity-50"
        >
          {{ submitting ? 'Сохранение...' : (adId ? 'Сохранить' : 'Создать объявление') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Импорты и логика будут добавлены в следующем шаге
import { ref, reactive, onMounted, computed, watch, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import type { AdvertisementFormData, AnimalFormData, FilterOptions, Species, AdPhoto as ExistingAdPhotoType, AdvertisementDetail } from '../types'; // Добавили AdvertisementDetail
import { useAuthStore } from '../stores/auth';

interface Breed { id: number; name: string; species: number; } // Для пород

const props = defineProps<{ id?: string; }>();
const router = useRouter();
const authStore = useAuthStore();
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const defaultAnimalData = { name: null, birth_date: null, species: null, breed: null, color: null, gender: null };
const formData = reactive<AdvertisementFormData>({
  title: '', description: '', status: null, latitude: null, longitude: null,
  animal_data: { ...defaultAnimalData },
  photos_upload: [],
});

const existingPhotos = ref<ExistingAdPhotoType[]>([]); // Для отображения фото при редактировании
const newPhotoFiles = ref<File[]>([]); // Файлы для новых фото
const newPhotoPreviews = ref<{ name: string; url: string }[]>([]);
const photosToDeleteIds = ref<number[]>([]); // ID существующих фото для удаления

const filterOptions = ref<FilterOptions>({
  regions: [], species: [], ad_statuses: [], colors: [], genders: [], age_categories: [],
});
const allBreeds = ref<Breed[]>([]); // Все породы для фильтрации на клиенте
const availableBreeds = computed(() => {
  if (!formData.animal_data.species || !allBreeds.value.length) return [];
  return allBreeds.value.filter(b => b.species === formData.animal_data.species);
});


const loadingInitialData = ref(false);
const initialError = ref<string | null>(null);
const submitting = ref(false);
const submitError = ref<string | null>(null);
const formErrors = ref<Record<string, any>>({});
const deletingAd = ref(false);

const adId = computed(() => props.id ? parseInt(props.id) : null);
const currentAdAuthorId = ref<number | null>(null);

const canDeleteCurrentAd = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || !adId.value) return false;
  if (authStore.user.is_staff) return true; // Админ Django
  if (authStore.user.role_permissions?.can_manage_any_advertisement) return true; // Модератор с правом управлять всеми
  // Владелец, если есть право удалять свои
  return authStore.user.id === currentAdAuthorId.value && authStore.user.role_permissions?.can_delete_own_advertisement;
});

const fetchFilterOptionsAndBreeds = async () => {
  // НЕ устанавливаем loadingInitialData.value = true; здесь, т.к. это часть общего процесса
  try {
    const [optionsRes, breedsRes] = await Promise.all([
      axios.get<FilterOptions>(`${API_BASE_URL}/filter-options/`),
      axios.get<any>(`${API_BASE_URL}/breeds/`)
    ]);
    filterOptions.value = optionsRes.data;

    if (Array.isArray(breedsRes.data)) {
      allBreeds.value = breedsRes.data as Breed[];
    } else if (breedsRes.data && Array.isArray(breedsRes.data.results)) {
      allBreeds.value = breedsRes.data.results as Breed[];
    } else {
      allBreeds.value = [];
      console.warn("Ответ от /api/breeds/ не является массивом или объектом с results:", breedsRes.data);
      // Можно установить initialError, если породы критичны
      // initialError.value = "Не удалось загрузить список пород.";
    }
  } catch (err) {
    console.error("Ошибка загрузки опций/пород:", err);
    initialError.value = "Не удалось загрузить данные для фильтров или список пород.";
    // Выбрасываем ошибку, чтобы onMounted мог ее поймать, если это критично
    throw err; 
  }
};

const fetchAdData = async () => {
  if (!adId.value) return;
  // loadingInitialData.value = true; // Перенесем управление этим флагом в onMounted
  // initialError.value = null; // Перенесем управление этим флагом в onMounted
  try {
    const response = await axios.get<AdvertisementDetail>(`${API_BASE_URL}/advertisements/${adId.value}/`);
    const ad = response.data;
    
    currentAdAuthorId.value = ad.user.id; // Если используется для прав удаления

    formData.title = ad.title;
    formData.description = ad.description;
    
    // Используем ID напрямую, если serializer возвращает ID для ForeignKey, иначе ищем по имени
    // Предположим, AdvertisementDetailSerializer возвращает ID для status
    // Если нет, то нужен find по filterOptions.ad_statuses
    const statusObj = filterOptions.value.ad_statuses.find(s => s.name === ad.status); // ad.status здесь - имя
    formData.status = statusObj ? statusObj.id : null;
    
    formData.latitude = ad.latitude;
    formData.longitude = ad.longitude;

    if (ad.animal) {
      formData.animal_data.name = ad.animal.name;
      formData.animal_data.birth_date = ad.animal.birth_date ? ad.animal.birth_date.split('T')[0] : null;
      
      const speciesObj = filterOptions.value.species.find(s => s.name === ad.animal.species); // ad.animal.species - имя
      formData.animal_data.species = speciesObj ? speciesObj.id : null;
      
      // Важно: selectedSpeciesChanged вызовет обновление availableBreeds
      // Это должно произойти ДО установки породы
      selectedSpeciesChanged(); // Вызываем, чтобы отфильтровать породы для текущего вида

      // Даем Vue время обновить computed свойство availableBreeds
      await nextTick(); // Импортируйте nextTick из 'vue'

      const breedObj = availableBreeds.value.find(b => b.name === ad.animal.breed); // ad.animal.breed - имя
      formData.animal_data.breed = breedObj ? breedObj.id : null;

      const colorObj = filterOptions.value.colors.find(c => c.name === ad.animal.color); // ad.animal.color - имя
      formData.animal_data.color = colorObj ? colorObj.id : null;

      const genderOption = filterOptions.value.genders.find(g => g.label === ad.animal.gender);
      formData.animal_data.gender = genderOption ? genderOption.value : null; // Устанавливаем value ('M', 'F', 'U')
    }
    existingPhotos.value = ad.photos || [];
    photosToDeleteIds.value = [];
    newPhotoFiles.value = [];
    newPhotoPreviews.value = [];

  } catch (err) {
    initialError.value = "Не удалось загрузить данные объявления для редактирования.";
    console.error("Fetch ad data error:", err);
  }
  // finally {
  //   loadingInitialData.value = false; // Перенесем
  // }
};

onMounted(async () => {
  loadingInitialData.value = true;
  initialError.value = null;
  try {
    // Сначала загружаем все опции для селектов
    await fetchFilterOptionsAndBreeds();
    // Затем, если это режим редактирования, загружаем данные объявления
    if (adId.value) {
      await fetchAdData();
    }
  } catch (err) {
    // Ошибка уже должна быть установлена в fetchFilterOptionsAndBreeds или fetchAdData
    if (!initialError.value) { // Если ошибка не была установлена ранее
        initialError.value = "Ошибка при инициализации формы.";
    }
  } finally {
    loadingInitialData.value = false;
  }
});

const selectedSpeciesChanged = async () => {
  formData.animal_data.breed = null; // Сбрасываем породу при смене вида
  // availableBreeds обновится автоматически через computed свойство
  // Если породы загружаются по API для конкретного вида:
  // if (formData.animal_data.species) {
  //   try {
  //     const response = await axios.get<Breed[]>(`${API_BASE_URL}/species/${formData.animal_data.species}/breeds/`);
  //     availableBreeds.value = response.data;
  //   } catch (error) { console.error("Error fetching breeds for species:", error); availableBreeds.value = []; }
  // } else {
  //   availableBreeds.value = [];
  // }
};

const handlePhotoUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files) {
    Array.from(target.files).forEach(file => {
      newPhotoFiles.value.push(file);
      newPhotoPreviews.value.push({ name: file.name, url: URL.createObjectURL(file) });
    });
    target.value = ''; // Сброс инпута для возможности выбора тех же файлов снова
  }
};

const removeNewPhoto = (index: number) => {
  URL.revokeObjectURL(newPhotoPreviews.value[index].url); // Освобождаем память
  newPhotoFiles.value.splice(index, 1);
  newPhotoPreviews.value.splice(index, 1);
};

const removeExistingPhoto = (photoId: number) => {
  existingPhotos.value = existingPhotos.value.filter(p => p.id !== photoId);
  if (!photosToDeleteIds.value.includes(photoId)) {
    photosToDeleteIds.value.push(photoId);
  }
};


const handleSubmit = async () => {
  submitting.value = true;
  submitError.value = null;
  formErrors.value = {};

  const payload = new FormData();
  payload.append('title', formData.title);
  payload.append('description', formData.description);
  if (formData.status) payload.append('status', String(formData.status));
  if (formData.latitude !== null) payload.append('latitude', String(formData.latitude));
  if (formData.longitude !== null) payload.append('longitude', String(formData.longitude));

  // Animal Data - DRF ожидает вложенные данные в формате animal_data.field_name
  // Если сервер настроен на прием `animal_data` как JSON строки, то:
  // payload.append('animal_data', JSON.stringify(formData.animal_data));
  // Но обычно для FormData вложенные объекты передаются так:
  if (formData.animal_data.name) payload.append('animal_data.name', formData.animal_data.name);
  if (formData.animal_data.birth_date) payload.append('animal_data.birth_date', formData.animal_data.birth_date);
  if (formData.animal_data.species) payload.append('animal_data.species', String(formData.animal_data.species));
  if (formData.animal_data.breed) payload.append('animal_data.breed', String(formData.animal_data.breed));
  if (formData.animal_data.color) payload.append('animal_data.color', String(formData.animal_data.color));
  if (formData.animal_data.gender) payload.append('animal_data.gender', String(formData.animal_data.gender));
  
  // Новые фото
  newPhotoFiles.value.forEach(file => {
    payload.append('photos_upload', file, file.name); // Ключ 'photos_upload' как в сериализаторе
  });

  // ID фото для удаления (если бэкенд это поддерживает через FormData)
  // photosToDeleteIds.value.forEach(id => payload.append('photos_to_delete_ids', String(id)));
  // Либо, если бэкенд ожидает список ID существующих фото, которые нужно СОХРАНИТЬ:
  // existingPhotos.value.forEach(photo => payload.append('existing_photo_ids', String(photo.id)));

  try {
    let response;
    const headers = { 'Content-Type': 'multipart/form-data' };

    if (adId.value) {
      // Если есть фото для удаления, возможно, нужен отдельный запрос или специальная обработка
      // Пока что отправляем все данные через PATCH
      if (photosToDeleteIds.value.length > 0) {
          // Дополнительный параметр для бэкенда, чтобы он знал, какие фото удалить
          photosToDeleteIds.value.forEach(id => payload.append('delete_photos', String(id)));
      }
      response = await axios.patch<AdvertisementDetail>(`${API_BASE_URL}/advertisements/${adId.value}/`, payload, { headers });
    } else {
      response = await axios.post<AdvertisementDetail>(`${API_BASE_URL}/advertisements/`, payload, { headers });
    }
    router.push({ name: 'AdvertisementDetail', params: { id: response.data.id } });
  } catch (err) {
    if (axios.isAxiosError(err) && err.response) {
      if (err.response.status === 400 && typeof err.response.data === 'object') {
        formErrors.value = err.response.data;
        submitError.value = "Пожалуйста, исправьте ошибки в форме.";
      } else {
        submitError.value = err.response.data?.detail || `Произошла ошибка (${err.response.statusText || err.response.status}).`;
      }
    } else {
      submitError.value = "Произошла неизвестная сетевая ошибка.";
    }
    console.error("Submit ad error:", err);
  } finally {
    submitting.value = false;
  }
};

const handleDeleteAd = async () => {
  if (!adId.value || !canDeleteCurrentAd.value) return;
  if (!confirm("Вы уверены, что хотите удалить это объявление? Это действие необратимо.")) return;

  deletingAd.value = true;
  submitError.value = null; // Сбрасываем общую ошибку формы
  try {
    await axios.delete(`${API_BASE_URL}/advertisements/${adId.value}/`);
    // После успешного удаления перенаправляем на страницу списка объявлений
    router.push({ name: 'Advertisements' });
    // Можно добавить сообщение об успехе через Pinia store или event bus, если нужно
  } catch (err) {
    if (axios.isAxiosError(err) && err.response) {
      submitError.value = err.response.data?.detail || `Ошибка удаления (${err.response.statusText || err.response.status}).`;
    } else {
      submitError.value = "Произошла неизвестная сетевая ошибка при удалении.";
    }
    console.error("Delete ad error:", err);
  } finally {
    deletingAd.value = false;
  }
};

onMounted(async () => {
  // Проверка прав (базовая, основная на бэке и в роутере)
  // if (!authStore.isAuthenticated || !authStore.user || (!authStore.user.is_staff && !authStore.user.role_permissions?.can_create_advertisement)) {
  //     // router.replace({ name: 'Home' }); // Или на страницу ошибки доступа
  //     // return; // Не загружать данные, если нет прав
  // }
  loadingInitialData.value = true;
  await fetchFilterOptionsAndBreeds(); // Загружаем опции и породы
  if (adId.value) {
    await fetchAdData(); // Затем данные объявления, если редактируем
  }
  loadingInitialData.value = false;
});

// Стили для инпутов и ошибок, можно вынести в <style>
const inputFieldClass = "w-full p-2 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500 text-sm";
const errorTextClass = "text-red-500 text-xs mt-1";

const availableStatusesForCreate = computed(() => {
  if (adId.value) return filterOptions.value.ad_statuses; // При редактировании доступны все (для модератора)

  // Если пользователь не админ/модератор
  if (!authStore.user?.is_staff && !authStore.user?.role_permissions?.can_manage_any_advertisement) {
    const allowedNames = ["Потеряно", "Найдено", "Отдам в добрые руки"]; // Пример
    return filterOptions.value.ad_statuses.filter(s => allowedNames.includes(s.name));
  }
  return filterOptions.value.ad_statuses; // Админ/модератор видят все
});

</script>

<style scoped>
.input-field {
  @apply p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm;
}
.error-text {
  @apply text-red-500 text-xs mt-1;
}
/* Дополнительные стили, если нужны */
</style>