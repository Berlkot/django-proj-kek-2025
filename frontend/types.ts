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
export interface AdAuthor { // Используем для автора объявления и автора отклика
  id: number;
  display_name: string;
  role: string | null; // Имя роли
  phone_number: string | null;
  email: string;
  avatar_url: string | null;
  region: { id: number; name: string } | null; // Предполагаем, что регион передается как объект или имя
}

export interface AdDetailAnimal {
  id: number;
  name: string | null;
  species: string;
  breed: string | null;
  color: string | null;
  gender: string | null;
  birth_date: string | null; // ISO
  age_years_months: string; // "1 год, 2 месяца"
}

export interface AdPhoto {
  id: number;
  image_url: string;
}

export interface AdResponse {
  id: number;
  user: AdAuthor; // Автор отклика
  message: string;
  date_created: string; // ISO
}

export interface AdvertisementDetail {
  id: number;
  title: string;
  description: string;
  animal: AdDetailAnimal;
  user: AdAuthor; // Автор объявления
  status: string; // Имя статуса (тип объявления)
  publication_date: string; // ISO
  latitude: number | null;
  longitude: number | null;
  photos: AdPhoto[];
  responses: AdResponse[];
  location: string; // Имя региона пользователя автора или "Не указано"
}