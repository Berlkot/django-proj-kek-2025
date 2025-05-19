export interface ArticleCategory {
  id: number;
  name: string;
  slug: string;
}

export interface Region {
  id: number;
  name: string;
}

export interface Species {
  id: number;
  name: string;
}

export interface AdStatus { // Для типа объявления
  id: number;
  name: string;
}

export interface AnimalColor {
  id: number;
  name: string;
}

export interface AnimalGender {
  id: number;
  name: string;
}

export interface AgeCategory {
  value: string; // e.g., "0_0.5"
  label: string; // e.g., "До 6 месяцев"
}

export interface FilterOptions {
  regions: Region[];
  species: Species[];
  ad_statuses: AdStatus[];
  colors: AnimalColor[];
  genders: AnimalGender[];
  age_categories: AgeCategory[];
}

export interface AdAnimal {
  name: string | null;
  species: string; // Имя вида
  breed: string | null; // Имя породы
  color: string | null; // Имя цвета
  gender: string | null; // Имя пола
  birth_date: string | null; // ISO строка даты
}

export interface AdUser {
  id: number;
  display_name: string;
  region: string | null; // Имя региона
}

export interface Advertisement {
  id: number;
  title: string;
  animal: AdAnimal;
  user: AdUser;
  status: string; // Имя статуса (типа объявления)
  short_description: string;
  publication_date: string; // ISO строка даты и времени
  latitude: number | null;
  longitude: number | null;
  first_photo_url: string | null;
  location: string; // Имя региона пользователя или "Не указано"
}

export interface PaginatedAdvertisementsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Advertisement[];
}

// Для хранения выбранных фильтров
export interface SelectedFilters {
  region: number | null;
  age_category: string | null;
  ad_status: number | null; // Тип объявления
  species: number | null; // Вид животного
  color: number | null;
  gender: number | null;
  // Добавьте другие по мере необходимости
}