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

export interface GenderOption {
    value: string; 
    label: string;
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
  genders: GenderOption[]; // <--- ИЗМЕНЕНО
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
  gender: string | null;
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

export interface RolePermissions {
  can_create_article?: boolean;
  can_edit_own_article?: boolean;
  can_edit_any_article?: boolean;
  can_delete_own_article?: boolean;
  can_delete_any_article?: boolean;
  can_edit_own_comment?: boolean;
  can_delete_own_comment?: boolean;
  can_delete_any_comment?: boolean;
  can_create_advertisement?: boolean;
  can_manage_own_advertisement?: boolean;
  can_manage_any_advertisement?: boolean;
  can_delete_own_advertisement?: boolean;
  can_delete_any_advertisement?: boolean;
}

export interface User {
  id: number;
  email: string;
  username: string;
  display_name?: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string | null;
  role?: string | null;
  region?: string | null;
  phone_number?: string | null;
  is_staff?: boolean;
  role_permissions?: RolePermissions | null;
}

export interface ArticleFormData {
  id?: number; // Для редактирования
  title: string;
  content: string;
  main_image: File | null; // Для загрузки нового файла
  main_image_url?: string | null; // Для отображения текущего изображения
  categories: number[]; // Массив ID категорий
}

export interface ArticleCategory { // Если еще не определен
  id: number;
  name: string;
  slug: string;
}


export interface AnimalFormData { // Для формы животного внутри объявления
  name: string | null;
  birth_date: string | null; // YYYY-MM-DD
  species: number | null; // ID
  breed: number | null; // ID
  color: number | null; // ID
  gender: string | null; // ID
}

export interface AdvertisementFormData {
  id?: number;
  title: string;
  description: string;
  status: number | null; // ID AdStatus
  latitude: number | null;
  longitude: number | null;
  animal_data: AnimalFormData;
  // Для управления фото
  photos_upload?: File[]; // Новые файлы для загрузки
  existing_photo_ids?: number[]; // ID существующих фото, которые нужно оставить/удалить (если используется такой механизм)
}
