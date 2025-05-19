# siteapp/management/commands/seed_db.py

import random
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker # Понадобится установить: pip install Faker
import os
from django.conf import settings
from django.core.files import File

from siteapp.models import (
    Region, Role, AdStatus, Species, Breed, Animal, Shelter,
    Advertisement, AdPhoto, Article # AdResponse и Comment можно генерировать позже или реже
)

User = get_user_model()
fake = Faker('ru_RU') # Используем русскую локализацию для Faker

class Command(BaseCommand):
    help = 'Seeds the database with initial data for development and testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # --- Очистка существующих данных (ОСТОРОЖНО!) ---
        # Раскомментируйте, если хотите очищать таблицы перед каждым запуском.
        # Это удалит ВСЕ ДАННЫЕ в указанных моделях.
        # Article.objects.all().delete()
        # AdPhoto.objects.all().delete()
        # Advertisement.objects.all().delete()
        # Animal.objects.all().delete()
        # Breed.objects.all().delete()
        # Species.objects.all().delete()
        # Shelter.objects.all().delete()
        # AdStatus.objects.all().delete()
        # User.objects.filter(is_superuser=False).delete() # Не удалять суперпользователей
        # Role.objects.all().delete()
        # Region.objects.all().delete()
        # self.stdout.write(self.style.WARNING('Existing data cleared (except superusers).'))

        # --- Создание базовых сущностей ---
        self.stdout.write('Creating Regions...')
        regions_data = ['Москва', 'Санкт-Петербург', 'Новосибирская область', 'Краснодарский край', 'Свердловская область', 'Ростовская область']
        regions = []
        for name in regions_data:
            region, created = Region.objects.get_or_create(name=name)
            regions.append(region)
            if created: self.stdout.write(f'  Created Region: {name}')

        self.stdout.write('Creating Roles...')
        roles_data = ['Пользователь', 'Волонтер', 'Администратор приюта', 'Модератор']
        roles = {} # Используем словарь для удобного доступа по имени
        for name in roles_data:
            role, created = Role.objects.get_or_create(name=name)
            roles[name] = role
            if created: self.stdout.write(f'  Created Role: {name}')

        self.stdout.write('Creating AdStatuses...')
        ad_statuses_data = ['Активно', 'Найдено', 'В архиве', 'Требует модерации']
        ad_statuses = {}
        for name in ad_statuses_data:
            status, created = AdStatus.objects.get_or_create(name=name)
            ad_statuses[name] = status
            if created: self.stdout.write(f'  Created AdStatus: {name}')

        self.stdout.write('Creating Species and Breeds...')
        species_breeds_data = {
            "Собака": ["Неизвестная порода", "Лабрадор ретривер", "Немецкая овчарка", "Дворняга", "Чихуахуа", "Йоркширский терьер"],
            "Кошка": ["Неизвестная порода", "Сиамская", "Мейн-кун", "Британская короткошерстная", "Сфинкс", "Домашняя короткошерстная"],
            "Птица": ["Неизвестный вид", "Попугай", "Канарейка"],
            "Грызун": ["Неизвестный вид", "Хомяк", "Морская свинка"],
        }
        species_map = {}
        breeds_map = {} # breeds_map['Собака'] = [объект_лабрадор, ...]
        for species_name, breed_names in species_breeds_data.items():
            species_obj, created = Species.objects.get_or_create(name=species_name)
            species_map[species_name] = species_obj
            breeds_map[species_name] = []
            if created: self.stdout.write(f'  Created Species: {species_name}')
            for breed_name in breed_names:
                breed_obj, created = Breed.objects.get_or_create(name=breed_name, species=species_obj)
                breeds_map[species_name].append(breed_obj)
                if created: self.stdout.write(f'    Created Breed: {breed_name} for {species_name}')

        # --- Создание Пользователей ---
        self.stdout.write('Creating Users...')
        num_users = 15
        created_users = []
        for i in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{fake.user_name()}{random.randint(1, 99)}"
            email = f"{username}@example.com"
            # Убедимся, что email уникален, если вдруг Faker сгенерирует одинаковый username
            while User.objects.filter(email=email).exists():
                 username = f"{fake.user_name()}{random.randint(100, 999)}"
                 email = f"{username}@example.com"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'display_name': f"{first_name} {last_name[0]}.",
                    'role': random.choice(list(roles.values())), # Случайная роль
                    'region': random.choice(regions),
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123') # Устанавливаем пароль для всех одинаковый для удобства
                user.save()
                created_users.append(user)
                self.stdout.write(f'  Created User: {email}')
            elif user not in created_users : # если пользователь был уже создан, но не в этой сессии
                created_users.append(user)

        if not created_users: # если все пользователи уже существуют
            created_users = list(User.objects.filter(is_superuser=False).order_by('?')[:num_users])


        # --- Создание Животных ---
        self.stdout.write('Creating Animals...')
        num_animals = 30
        created_animals = []
        for _ in range(num_animals):
            species_name = random.choice(list(species_map.keys()))
            species_obj = species_map[species_name]
            breed_obj = random.choice(breeds_map[species_name])
            animal_name = fake.first_name_female() if species_name == "Кошка" else fake.first_name_male() # Клички

            animal = Animal.objects.create(
                name=animal_name,
                birth_date=fake.date_between(start_date='-5y', end_date='-1m'), # Возраст от месяца до 5 лет
                species=species_obj,
                breed=breed_obj
            )
            created_animals.append(animal)
            self.stdout.write(f'  Created Animal: {animal_name} ({species_obj.name})')

        # --- Создание Приютов ---
        self.stdout.write('Creating Shelters...')
        num_shelters = 5
        shelter_names = ["Ласка", "Добрый дом", "Четыре лапы", "Надежда", "Верный друг"]
        created_shelters = []
        for i in range(num_shelters):
            name = f"Приют \"{random.choice(shelter_names)} {fake.city_name().split(' ')[-1]}\"" # Приют "Ласка Московский"
            shelter, created = Shelter.objects.get_or_create(
                name=name,
                defaults={
                    'address': fake.address(),
                    'contacts': f"Телефон: {fake.phone_number()}\nEmail: {fake.email()}",
                    'region': random.choice(regions)
                }
            )
            if created:
                created_shelters.append(shelter)
                self.stdout.write(f'  Created Shelter: {name}')

        # --- Создание Объявлений ---
        self.stdout.write('Creating Advertisements...')
        num_ads = 20
        if not created_users: # Если не было создано новых пользователей, возьмем существующих
            users_for_ads = list(User.objects.filter(is_superuser=False).order_by('?')[:num_ads])
        else:
            users_for_ads = created_users

        if not users_for_ads:
            self.stdout.write(self.style.WARNING('No users available to create advertisements.'))
        else:
            for i in range(min(num_ads, len(created_animals))): # Не больше чем есть животных
                user = random.choice(users_for_ads)
                animal = created_animals[i] # Берем по одному животному для каждого объявления, чтобы не было дублей

                # Устанавливаем дату публикации от сейчас до 30 дней назад
                pub_date = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0,23))

                ad_title_options = [
                    f"Потерялась {animal.species.name.lower()} {animal.name or ''}!",
                    f"Найдена {animal.species.name.lower()} в районе {user.region.name if user.region else 'неизвестном'}",
                    f"Ищу хозяина для {animal.species.name.lower()}",
                    f"Срочно! {animal.species.name.lower()} {animal.name or ''} нуждается в помощи!"
                ]

                ad = Advertisement.objects.create(
                    user=user,
                    animal=animal,
                    status=ad_statuses.get('Активно', AdStatus.objects.first()), # Статус "Активно"
                    title=random.choice(ad_title_options),
                    description=fake.paragraph(nb_sentences=random.randint(3, 7)),
                    publication_date=pub_date, # Переопределяем auto_now_add для сидинга
                    latitude=float(fake.latitude()) if random.choice([True, False]) else None,
                    longitude=float(fake.longitude()) if random.choice([True, False]) else None,
                )
                # Сразу же обновляем publication_date, т.к. auto_now_add устанавливает его при создании
                Advertisement.objects.filter(pk=ad.pk).update(publication_date=pub_date)

                # Добавляем фото (1-3 фото на объявление)
                # Для AdPhoto нужно, чтобы у вас были настроены MEDIA_ROOT и MEDIA_URL
                # и желательно иметь какие-то placeholder картинки или генерировать их.
                # Здесь мы не будем создавать реальные файлы, а просто создадим записи.
                # В реальном проекте вам нужно будет положить файлы в `media/ad_photos/...`
                # или использовать библиотеку типа `django-imagekit` с генерацией плейсхолдеров.
                num_photos = random.randint(0, 3)
                for _ in range(num_photos):
                    placeholder_dir = os.path.join(settings.MEDIA_ROOT, 'seed_placeholders')
                    if os.path.exists(placeholder_dir) and os.listdir(placeholder_dir):
                        placeholder_image_name = random.choice(os.listdir(placeholder_dir))
                        placeholder_image_path = os.path.join(placeholder_dir, placeholder_image_name)
                        with open(placeholder_image_path, 'rb') as f:
                            django_file = File(f, name=placeholder_image_name)
                            AdPhoto.objects.create(advertisement=ad, image=django_file)
                            self.stdout.write(f'    Added photo {placeholder_image_name} for Ad ID {ad.id}')
                    else:
                        self.stdout.write(f'    Skipped photo for Ad ID {ad.id} (placeholder dir empty or not found)')


                self.stdout.write(f'  Created Ad: "{ad.title}" by {user.email}')

        # --- Создание Статей ---
        self.stdout.write('Creating Articles...')
        num_articles = 10
        if not users_for_ads: # Используем тех же юзеров, если есть
             users_for_articles = list(User.objects.filter(is_staff=True).order_by('?')[:5]) # Статьи от админов/стаффа
             if not users_for_articles:
                 users_for_articles = list(User.objects.filter(is_superuser=False).order_by('?')[:5])
        else:
            users_for_articles = [u for u in users_for_ads if u.is_staff or u.role.name == 'Модератор'][:5] # Предпочитаем стафф
            if not users_for_articles and users_for_ads: # Если нет стаффа, берем любых
                users_for_articles = random.sample(users_for_ads, min(len(users_for_ads), 5))


        if not users_for_articles:
            self.stdout.write(self.style.WARNING('No suitable users found to author articles. Skipping article creation.'))
        else:
            article_titles = [
                "Как ухаживать за котенком: полное руководство",
                "Топ-10 пород собак для семей с детьми",
                "Первая помощь при отравлении у животных",
                "Волонтерство в приюте: как помочь?",
                "Стерилизация и кастрация: за и против",
                "Выбираем корм для вашей собаки: советы ветеринара",
                "Почему кошки мурлычут? Раскрываем тайны",
                "Дрессировка щенка: основные команды",
                "Как подготовить дом к появлению нового питомца",
                "Зимний уход за животными: важные аспекты"
            ]
            for i in range(min(num_articles, len(article_titles))):
                pub_date = timezone.now() - timedelta(days=random.randint(0, 180), hours=random.randint(0,23))
                article = Article.objects.create(
                    title=article_titles[i],
                    content="\n\n".join(fake.paragraphs(nb=random.randint(5, 15))), # Объединяем параграфы в одну строку
                    author=random.choice(users_for_articles),
                    publication_date=pub_date
                )
                Article.objects.filter(pk=article.pk).update(publication_date=pub_date) # Обновляем дату
                self.stdout.write(f'  Created Article: "{article.title}"')

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))