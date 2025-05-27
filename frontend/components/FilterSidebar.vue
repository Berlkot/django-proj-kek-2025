<template>
  <aside class="bg-white p-5 rounded-lg shadow w-full">
    <h3 class="text-xl font-semibold text-gray-800 mb-4">Фильтры</h3>
    <form>
      <div class="mb-4">
        <label for="filter-region" class="block text-sm font-medium text-gray-700 mb-1">Город/Область</label>
        <select id="filter-region" :value="internalFilters.region === null ? 'null_option' : internalFilters.region"
          @change="updateFilter('region', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Все регионы</option>
          <option v-for="region in options.regions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>
      </div>


      <div class="mb-4">
        <label for="filter-age" class="block text-sm font-medium text-gray-700 mb-1">Возраст</label>
        <select id="filter-age"
          :value="internalFilters.age_category === null ? 'null_option' : internalFilters.age_category"
          @change="updateFilter('age_category', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Любой возраст</option>
          <option v-for="age in options.age_categories" :key="age.value" :value="age.value">
            {{ age.label }}
          </option>
        </select>
      </div>


      <div class="mb-4">
        <label for="filter-ad-type" class="block text-sm font-medium text-gray-700 mb-1">Тип объявления</label>
        <select id="filter-ad-type"
          :value="internalFilters.ad_status === null ? 'null_option' : internalFilters.ad_status"
          @change="updateFilter('ad_status', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Все типы</option>
          <option v-for="status in options.ad_statuses" :key="status.id" :value="status.id">
            {{ status.name }}
          </option>
        </select>
      </div>


      <div class="mb-4">
        <label for="filter-species" class="block text-sm font-medium text-gray-700 mb-1">Вид животного</label>
        <select id="filter-species" :value="internalFilters.species === null ? 'null_option' : internalFilters.species"
          @change="updateFilter('species', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Все виды</option>
          <option v-for="specie in options.species" :key="specie.id" :value="specie.id">
            {{ specie.name }}
          </option>
        </select>
      </div>


      <div class="mb-4">
        <label for="filter-color" class="block text-sm font-medium text-gray-700 mb-1">Окрас</label>
        <select id="filter-color" :value="internalFilters.color === null ? 'null_option' : internalFilters.color"
          @change="updateFilter('color', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Любой окрас</option>
          <option v-for="color in options.colors" :key="color.id" :value="color.id">
            {{ color.name }}
          </option>
        </select>
      </div>

      <div class="mb-4">
        <label for="filter-gender" class="block text-sm font-medium text-gray-700 mb-1">Пол питомца</label>
        <select id="filter-gender" :value="internalFilters.gender === null ? 'null_option' : internalFilters.gender"
          @change="updateFilter('gender', ($event.target as HTMLSelectElement).value)"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 text-sm">
          <option value="null_option">Любой пол</option>
          <option v-for="gender in options.genders" :key="gender.value" :value="gender.value">
            {{ gender.label }}
          </option>
        </select>
      </div>

      <div class="mt-6">
        <button type="button" @click="$emit('apply-filters', { ...internalFilters })"
          class="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-2 px-4 rounded-md transition duration-150">
          Применить
        </button>
        <button type="button" @click="resetInternalFiltersAndEmit"
          class="mt-2 w-full bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 px-4 rounded-md transition duration-150">
          Сбросить фильтры
        </button>
      </div>
    </form>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch, toRaw } from 'vue';
import type { FilterOptions, SelectedFilters } from '../types';

const props = defineProps<{
  options: FilterOptions;
  modelValue: SelectedFilters;
}>();


const emit = defineEmits(['apply-filters', 'reset-filters']);


const internalFilters = ref<SelectedFilters>({ ...toRaw(props.modelValue) });


watch(() => props.modelValue, (newValue) => {

  console.log(newValue);
  if (JSON.stringify(toRaw(newValue)) !== JSON.stringify(toRaw(internalFilters.value))) {
    internalFilters.value = { ...toRaw(newValue) };
  }
}, { deep: true });

const updateFilter = (key: keyof SelectedFilters, eventTargetValue: string) => {
  let processedValue: string | number | null = null;

  if (eventTargetValue === 'null_option') {
    processedValue = null;
  } else if (key !== 'age_category' && key !== 'gender') {
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


const resetInternalFiltersAndEmit = () => {
  const defaultRawFilters: SelectedFilters = {
    region: null, age_category: null, ad_status: null,
    species: null, color: null, gender: null
  };
  internalFilters.value = { ...defaultRawFilters };
  emit('reset-filters');
};

</script>
