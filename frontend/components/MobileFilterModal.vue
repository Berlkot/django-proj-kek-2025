<template>
  <Transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0"
    enter-to-class="opacity-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100"
    leave-to-class="opacity-0">
    <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-75 z-40 flex justify-center items-end sm:items-center"
      @click.self="closeModal" 
      >
      <Transition enter-active-class="transition ease-out duration-300"
        enter-from-class="opacity-0 translate-y-full sm:translate-y-10 sm:scale-95"
        enter-to-class="opacity-100 translate-y-0 sm:scale-100" leave-active-class="transition ease-in duration-200"
        leave-from-class="opacity-100 translate-y-0 sm:scale-100"
        leave-to-class="opacity-0 translate-y-full sm:translate-y-10 sm:scale-95">
        <div v-if="isOpen"
          class="bg-white w-full max-w-md max-h-[90vh] sm:max-h-[80vh] rounded-t-lg sm:rounded-lg shadow-xl overflow-hidden flex flex-col"
          role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <!-- Заголовок модального окна -->
          <div class="p-4 border-b border-gray-200 flex justify-between items-center sticky top-0 bg-white z-10">
            <h2 id="modal-title" class="text-lg font-semibold text-gray-800">Фильтры</h2>
            <button @click="closeModal"
              class="text-gray-400 hover:text-gray-600 p-1 rounded-full focus:outline-none focus:ring-2 focus:ring-green-500"
              aria-label="Закрыть фильтры">
              <font-awesome-icon :icon="['fas', 'times']" class="w-5 h-5" />
            </button>
          </div>

          <!-- Контент с фильтрами (прокручиваемый) -->
          <div class="p-4 flex-grow overflow-y-auto">
            <form @submit.prevent="applyAndClose">
              <!-- Город/Область -->
              <div class="mb-4">
                <label for="modal-filter-region" class="block text-sm font-medium text-gray-700 mb-1">Город/Область</label>
                <!-- Отображаем select только если есть опции -->
                <select
                  v-if="options.regions && options.regions.length > 0"
                  id="modal-filter-region"
                  :value="internalFilters.region === null ? 'null_option' : internalFilters.region"
                  @change="updateFilter('region', ($event.target as HTMLSelectElement).value)"
                  class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                >
                  <option value="null_option">Все регионы</option>
                  <option v-for="region in options.regions" :key="region.id" :value="region.id">
                    {{ region.name }}
                  </option>
                </select>
                <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                  Загрузка регионов...
                </div>
              </div>

              <!-- Возраст -->
              <div class="mb-4">
                <label for="modal-filter-age" class="block text-sm font-medium text-gray-700 mb-1">Возраст</label>
                <select
                  v-if="options.age_categories && options.age_categories.length > 0"
                  id="modal-filter-age"
                  :value="internalFilters.age_category === null ? 'null_option' : internalFilters.age_category"
                  @change="updateFilter('age_category', ($event.target as HTMLSelectElement).value)"
                  class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                >
                  <option value="null_option">Любой возраст</option>
                  <option v-for="age in options.age_categories" :key="age.value" :value="age.value">
                    {{ age.label }}
                  </option>
                </select>
                <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                  Загрузка категорий возраста...
                </div>
              </div>

              <!-- Тип объявления -->
              <div class="mb-4">
                  <label for="modal-filter-ad-type" class="block text-sm font-medium text-gray-700 mb-1">Тип объявления</label>
                  <select
                      v-if="options.ad_statuses && options.ad_statuses.length > 0"
                      id="modal-filter-ad-type"
                      :value="internalFilters.ad_status === null ? 'null_option' : internalFilters.ad_status"
                      @change="updateFilter('ad_status', ($event.target as HTMLSelectElement).value)"
                      class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                  >
                      <option value="null_option">Все типы</option>
                      <option v-for="status in options.ad_statuses" :key="status.id" :value="status.id">{{ status.name }}</option>
                  </select>
                  <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                      Загрузка типов объявлений...
                  </div>
              </div>

              <!-- Вид животного -->
              <div class="mb-4">
                  <label for="modal-filter-species" class="block text-sm font-medium text-gray-700 mb-1">Вид животного</label>
                  <select
                      v-if="options.species && options.species.length > 0"
                      id="modal-filter-species"
                      :value="internalFilters.species === null ? 'null_option' : internalFilters.species"
                      @change="updateFilter('species', ($event.target as HTMLSelectElement).value)"
                      class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                  >
                      <option value="null_option">Все виды</option>
                      <option v-for="specie in options.species" :key="specie.id" :value="specie.id">{{ specie.name }}</option>
                  </select>
                  <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                      Загрузка видов животных...
                  </div>
              </div>

              <!-- Окрас (colors может быть пустым, если не загружено) -->
              <div class="mb-4">
                  <label for="modal-filter-color" class="block text-sm font-medium text-gray-700 mb-1">Окрас</label>
                  <select
                      v-if="options.colors"
                      id="modal-filter-color"
                      :value="internalFilters.color === null ? 'null_option' : internalFilters.color"
                      @change="updateFilter('color', ($event.target as HTMLSelectElement).value)"
                      class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                  >
                      <option value="null_option">Любой окрас</option>
                      <option v-for="color in options.colors" :key="color.id" :value="color.id">{{ color.name }}</option>
                  </select>
                   <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                      Загрузка окрасов...
                  </div>
              </div>

              <!-- Пол питомца (genders может быть пустым) -->
              <div class="mb-4">
                  <label for="modal-filter-gender" class="block text-sm font-medium text-gray-700 mb-1">Пол питомца</label>
                  <select
                      v-if="options.genders"
                      id="modal-filter-gender"
                      :value="internalFilters.gender === null ? 'null_option' : internalFilters.gender"
                      @change="updateFilter('gender', ($event.target as HTMLSelectElement).value)"
                      class="w-full p-2.5 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm bg-white"
                  >
                      <option value="null_option">Любой пол</option>
                      <option v-for="gender in options.genders" :key="gender.id" :value="gender.id">{{ gender.name }}</option>
                  </select>
                  <div v-else class="w-full p-2.5 border border-gray-300 rounded-md bg-gray-100 text-gray-500 text-sm">
                      Загрузка пола...
                  </div>
              </div>
            </form>
          </div>

          <!-- Футер с кнопками -->
          <div class="p-4 border-t border-gray-200 sticky bottom-0 bg-white z-10 space-y-2">
            <button @click="applyAndClose"
              class="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-4 rounded-md transition duration-150 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50">
              Показать результаты
            </button>
            <button @click="resetAndApply"
              class="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2.5 px-4 rounded-md transition duration-150 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400">
              Сбросить и показать
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
// Скриптовая часть MobileFilterModal.vue остается такой же, как в предыдущем ответе.
// Убираем computed `hasOptions`, так как проверки теперь в шаблоне.
import { ref, watch, toRaw, onMounted, onUnmounted } from 'vue';
import type { FilterOptions, SelectedFilters } from '../types';

const props = defineProps<{
  isOpen: boolean;
  options: FilterOptions;
  modelValue: SelectedFilters;
}>();

const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void;
  (e: 'apply-filters', filters: SelectedFilters): void;
  (e: 'reset-filters'): void;
}>();

const internalFilters = ref<SelectedFilters>({ ...toRaw(props.modelValue) });

watch(() => props.modelValue, (newValue) => {
  if (JSON.stringify(toRaw(newValue)) !== JSON.stringify(toRaw(internalFilters.value))) {
    internalFilters.value = { ...toRaw(newValue) };
  }
}, { deep: true });

const updateFilter = (key: keyof SelectedFilters, eventTargetValue: string) => {
  let processedValue: string | number | null = null;
  if (eventTargetValue === 'null_option') {
    processedValue = null;
  } else if (key !== 'age_category') {
    const numValue = parseInt(eventTargetValue, 10);
    processedValue = isNaN(numValue) ? null : numValue;
  } else {
    processedValue = eventTargetValue;
  }
  internalFilters.value = {
    ...internalFilters.value,
    [key]: processedValue,
  };
};

const closeModal = () => { emit('update:isOpen', false); };

const applyAndClose = () => {
  emit('apply-filters', { ...toRaw(internalFilters.value) });
  closeModal();
};

const resetAndApply = () => {
  const defaultRawFilters: SelectedFilters = {
    region: null, age_category: null, ad_status: null,
    species: null, color: null, gender: null
  };
  internalFilters.value = { ...defaultRawFilters };
  emit('reset-filters');
  closeModal();
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.isOpen) {
    closeModal();
  }
};
onMounted(() => { document.addEventListener('keydown', handleKeydown); });
onUnmounted(() => { document.removeEventListener('keydown', handleKeydown); });
</script>
<style scoped>
/* Стили для улучшения прокрутки, если потребуется */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  /* gray-300 */
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background-color: #94a3b8;
  /* gray-500 */
}
</style>
