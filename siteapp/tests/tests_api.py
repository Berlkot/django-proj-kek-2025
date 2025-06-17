from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from ..models import (
    User, Role, Region, Species, Breed, AdStatus,
    Animal, Advertisement, AdResponse, AdvertisementRating
)

class ModelTests(TestCase):

    def setUp(self):
        """Настройка данных для тестов моделей."""
        self.species_cat = Species.objects.create(name="Кошка")
        self.status_lost = AdStatus.objects.create(name="Потеряно")
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_advertisement_model_validation(self):
        """
        1. Тест: Модель Advertisement не может быть создана без обязательных полей.
        """
        animal = Animal.objects.create(species=self.species_cat)

        with self.assertRaises(Exception):
            Advertisement.objects.create(animal=animal, status=self.status_lost, title="Test Ad")

        with self.assertRaises(Exception):
            Advertisement.objects.create(user=self.user, status=self.status_lost, title="Test Ad")

        with self.assertRaises(Exception):
            Advertisement.objects.create(user=self.user, animal=animal, title="Test Ad")

    def test_animal_age_calculation(self):
        """
        2. Тест: Проверка вычисления возраста животного в модели Animal.
        """
        today = timezone.now().date()

        birth_date_1 = today - relativedelta(years=1, months=2)
        animal1 = Animal.objects.create(species=self.species_cat, birth_date=birth_date_1)
        delta1 = relativedelta(today, animal1.birth_date)
        self.assertEqual(delta1.years, 1)
        self.assertEqual(delta1.months, 2)

        birth_date_2 = today - relativedelta(months=5)
        animal2 = Animal.objects.create(species=self.species_cat, birth_date=birth_date_2)
        delta2 = relativedelta(today, animal2.birth_date)
        self.assertEqual(delta2.years, 0)
        self.assertEqual(delta2.months, 5)

        animal3 = Animal.objects.create(species=self.species_cat, birth_date=None)
        self.assertIsNone(animal3.birth_date)


class ApiTests(APITestCase):

    def setUp(self):
        """Настройка данных для тестов API."""
        self.client = APIClient()

        self.user_role = Role.objects.create(name="Пользователь", can_create_advertisement=True)
        self.user = User.objects.create_user(
            username='testuser',
            email='api@test.com',
            password='password123',
            role=self.user_role
        )
        self.admin = User.objects.create_superuser(username='admin', email='admin@test.com', password='password123')

        response = self.client.post(reverse('jwt-create'), {'email': 'api@test.com', 'password': 'password123'}, format='json')
        self.access_token = response.data['access']

        self.region_msk = Region.objects.create(name="Москва")
        self.region_spb = Region.objects.create(name="Санкт-Петербург")
        self.species_cat = Species.objects.create(name="Кошка")
        self.species_dog = Species.objects.create(name="Собака")
        self.status_lost = AdStatus.objects.create(name="Потеряно")
        self.status_found = AdStatus.objects.create(name="Найдено")

        self.user.region = self.region_msk
        self.user.save()

        animal1 = Animal.objects.create(species=self.species_cat, name="Мурка")
        self.ad1 = Advertisement.objects.create(user=self.user, animal=animal1, status=self.status_lost, title="Пропала кошка Мурка")

        animal2 = Animal.objects.create(species=self.species_dog, name="Шарик")
        self.ad2 = Advertisement.objects.create(user=self.user, animal=animal2, status=self.status_found, title="Найден пес Шарик")

        user_spb = User.objects.create_user(username='spbuser', email='spb@test.com', password='password123', region=self.region_spb)
        animal3 = Animal.objects.create(species=self.species_cat, name="Барсик")
        self.ad3 = Advertisement.objects.create(user=user_spb, animal=animal3, status=self.status_lost, title="Пропал кот Барсик в СПб")


    def test_list_advertisements_unauthenticated(self):
        """
        3. Тест: Представление AdvertisementViewSet (list) возвращает корректный список объявлений (200 OK).
        """
        url = reverse('advertisement-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 3)

    def test_list_advertisements_correct_fields(self):
        """
        4. Тест: Представление AdvertisementViewSet (list) возвращает корректные поля.
        """
        url = reverse('advertisement-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_ad_in_response = response.data['results'][0]
        expected_keys = [
            'id', 'title', 'animal', 'user', 'status', 'short_description',
            'publication_date', 'first_photo_url', 'location', 'comments_count', 'average_rating'
        ]
        for key in expected_keys:
            self.assertIn(key, first_ad_in_response.keys())

    def test_retrieve_advertisement_detail(self):
        """
        5. Тест: Представление AdvertisementViewSet (retrieve) возвращает детальную информацию.
        """
        url = reverse('advertisement-detail', kwargs={'pk': self.ad1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.ad1.id)
        self.assertEqual(response.data['title'], "Пропала кошка Мурка")
        self.assertIn('responses', response.data)

    def test_create_advertisement_authenticated(self):
        """
        6. Тест: Создание объявления авторизованным пользователем.
        """
        url = reverse('advertisement-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        breed_main_coon = Breed.objects.create(species=self.species_cat, name="Мейн-кун")

        data = {
            "title": "Новое объявление о коте",
            "description": "Очень детальное описание.",
            "status": self.status_lost.id,
            "animal_data": {
                "name": "Пушок",
                "species": self.species_cat.id,
                "breed": breed_main_coon.id
            }
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Advertisement.objects.count(), 4)

        new_ad = Advertisement.objects.get(id=response.data['id'])
        self.assertEqual(new_ad.title, "Новое объявление о коте")
        self.assertEqual(new_ad.animal.name, "Пушок")

    def test_create_advertisement_unauthenticated(self):
        """
        7. Тест: Попытка создания объявления неавторизованным пользователем.
        """
        url = reverse('advertisement-list')
        self.client.credentials()
        data = {"title": "Попытка создать", "description": "...", "status": self.status_lost.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Advertisement.objects.count(), 3)

    def test_advertisement_filter_by_species(self):
        """
        8. Тест: Фильтрация объявлений по виду животного (Кошка).
        """
        url = reverse('advertisement-list') + f'?species={self.species_cat.id}'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        for ad_data in response.data['results']:
            self.assertEqual(ad_data['animal']['species'], self.species_cat.name)

    def test_advertisement_filter_by_location(self):
        """
        9. Тест: Фильтрация объявлений по местоположению (региону).
        """
        url = reverse('advertisement-list') + f'?region={self.region_spb.id}'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.ad3.id)
        self.assertEqual(response.data['results'][0]['location'], "Санкт-Петербург")

    def test_add_response_to_advertisement(self):
        """
        10. Тест: Добавление комментария (отклика) к объявлению.
        """
        url = reverse('ad_response_create', kwargs={'ad_id': self.ad1.id})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {"message": "Это тестовый комментарий."}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Это тестовый комментарий.")
        self.assertEqual(AdResponse.objects.count(), 1)
        self.assertEqual(AdResponse.objects.first().advertisement, self.ad1)
