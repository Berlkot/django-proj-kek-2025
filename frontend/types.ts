export interface ArticleCategory {
  id: number
  name: string
  slug: string
}

export interface Region {
  id: number
  name: string
}

export interface Species {
  id: number
  name: string
}

export interface AdStatus {
  id: number
  name: string
}

export interface AnimalColor {
  id: number
  name: string
}

export interface GenderOption {
  value: string
  label: string
}

export interface AgeCategory {
  value: string
  label: string
}

export interface FilterOptions {
  regions: Region[]
  species: Species[]
  ad_statuses: AdStatus[]
  colors: AnimalColor[]
  genders: GenderOption[]
  age_categories: AgeCategory[]
  breeds: Breed[]
}

export interface AdAnimal {
  name: string | null
  species: string
  breed: string | null
  color: string | null
  gender: string | null
  birth_date: string | null
}

export interface AdUser {
  id: number
  display_name: string
  region: string | null
}

export interface Advertisement {
  id: number
  title: string
  animal: AdAnimal
  user: AdUser
  status: string
  short_description: string
  publication_date: string
  latitude: number | null
  longitude: number | null
  first_photo_url: string | null
  location: string
}

export interface PaginatedAdvertisementsResponse {
  count: number
  next: string | null
  previous: string | null
  results: Advertisement[]
}

export interface SelectedFilters {
  region: number | null
  age_category: string | null
  ad_status: number | null
  species: number | null
  breed: number | null
  color: number | null
  gender: string | null
  publication_date_after: string | null
  publication_date_before: string | null
}
export interface AdAuthor {
  id: number
  display_name: string
  role: string | null
  phone_number: string | null
  email: string
  avatar_url: string | null
  region: { id: number; name: string } | null
}

export interface AdDetailAnimal {
  id: number
  name: string | null
  species: string
  breed: string | null
  color: string | null
  gender: string | null
  birth_date: string | null
  age_years_months: string
}

export interface AdPhoto {
  id: number
  image_url: string
}

export interface AdResponse {
  id: number
  user: AdAuthor
  message: string
  date_created: string
}

export interface AdvertisementDetail {
  id: number
  title: string
  description: string
  animal: AdDetailAnimal
  user: AdAuthor
  status: string
  publication_date: string
  latitude: number | null
  longitude: number | null
  photos: AdPhoto[]
  responses: AdResponse[]
  location: string
}

export interface RolePermissions {
  can_create_article?: boolean
  can_edit_own_article?: boolean
  can_edit_any_article?: boolean
  can_delete_own_article?: boolean
  can_delete_any_article?: boolean
  can_edit_own_comment?: boolean
  can_delete_own_comment?: boolean
  can_delete_any_comment?: boolean
  can_create_advertisement?: boolean
  can_edit_own_advertisement?: boolean
  can_manage_any_advertisement?: boolean
  can_delete_own_advertisement?: boolean
  can_delete_any_advertisement?: boolean
}

export interface User {
  id: number
  email: string
  username: string
  display_name?: string
  first_name?: string
  last_name?: string
  avatar_url?: string | null
  role?: string | null
  region?: string | null
  phone_number?: string | null
  is_staff?: boolean
  role_permissions?: RolePermissions | null
}

export interface ArticleFormData {
  id?: number
  title: string
  content: string
  main_image: File | null
  main_image_url?: string | null
  categories: number[]
}

export interface ArticleCategory {
  id: number
  name: string
  slug: string
}

export interface AnimalFormData {
  name: string | null
  birth_date: string | null
  species: number | null
  breed: number | null
  color: number | null
  gender: string | null
}

export interface AdvertisementFormData {
  id?: number
  title: string
  description: string
  status: number | null
  latitude: number | null
  longitude: number | null
  animal_data: AnimalFormData

  photos_upload?: File[]
  existing_photo_ids?: number[]
}

export interface Breed {
  id: number
  name: string
  species_id: number
}

export interface AdvertisementRating {
  id: number
  user_id: number
  advertisement_id: number
  rating: number
}

export interface Role {
  id: number
  name: string
}

// НОВЫЙ ИНТЕРФЕЙС
export interface ProfileUser {
  id: number
  email: string
  username: string
  display_name?: string
  first_name?: string
  last_name?: string
  avatar_url?: string | null
  role_name?: string | null
  region_name?: string | null
  phone_number?: string | null
  date_joined: string
  is_staff?: boolean
}

// НОВЫЙ ИНТЕРФЕЙС
export interface ProfileData {
  user: ProfileUser
  advertisements: Advertisement[] // Используем существующий тип Advertisement
}

// НОВЫЙ ИНТЕРФЕЙС
export interface ProfileFormData {
  display_name: string
  first_name: string
  last_name: string
  phone_number: string | null
  region: number | null
  avatar: File | null
  email: string
  role?: number | null
  is_staff?: boolean
}

export interface AdminUser {
  id: number
  email: string
  username: string
  display_name: string
  role_name: string | null
  region_name: string | null
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

export interface PaginatedAdminUsersResponse {
  count: number
  next: string | null
  previous: string | null
  results: AdminUser[]
}
