# siteapp/filters.py
import django_filters
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Advertisement, Animal, Region, AdStatus, AnimalGender, Species, AnimalColor
from django.db.models import Q

# Возрастные категории для фильтра
AGE_CHOICES = [
    ('0_0.5', 'До 6 месяцев'),      # от 0 до 6 месяцев
    ('0.5_1', '6-12 месяцев'),     # от 6 до 12 месяцев
    ('1_3', '1-3 года'),           # от 1 до 3 лет
    ('3_7', '3-7 лет'),           # от 3 до 7 лет
    ('7_inf', 'Старше 7 лет'),     # старше 7 лет
    ('unknown', 'Возраст неизвестен'),
]

class AdvertisementFilter(django_filters.FilterSet):
    # Фильтр по региону пользователя, создавшего объявление
    region = django_filters.ModelChoiceFilter(
        field_name='user__region',
        queryset=Region.objects.all(),
        label='Регион'
    )
    # Фильтр по типу объявления (статусу)
    ad_status = django_filters.ModelChoiceFilter(
        field_name='status',
        queryset=AdStatus.objects.all(),
        label='Тип объявления'
    )
    # Фильтры по животному
    species = django_filters.ModelChoiceFilter(
        field_name='animal__species',
        queryset=Species.objects.all(),
        label='Вид животного'
    )
    gender = django_filters.ModelChoiceFilter(
        field_name='animal__gender',
        queryset=AnimalGender.objects.all(),
        label='Пол'
    )
    color = django_filters.ModelChoiceFilter(
        field_name='animal__color',
        queryset=AnimalColor.objects.all(),
        label='Окрас'
    )
    # Фильтр по возрасту
    age_category = django_filters.ChoiceFilter(
        choices=AGE_CHOICES,
        method='filter_by_age_category',
        label='Возраст'
    )

    # Поиск по заголовку и описанию объявления, имени животного
    search = django_filters.CharFilter(method='global_search', label="Поиск")


    class Meta:
        model = Advertisement
        fields = ['region', 'ad_status', 'species', 'gender', 'color', 'age_category', 'search']

    def filter_by_age_category(self, queryset, name, value):
        now = timezone.now().date()
        if value == 'unknown':
            return queryset.filter(animal__birth_date__isnull=True)
        
        min_age_delta, max_age_delta = None, None

        if value == '0_0.5': # до 6 мес
            min_age_delta = relativedelta(months=0)
            max_age_delta = relativedelta(months=6)
            # Животные, рожденные от (now - 6 месяцев) до now
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == '0.5_1': # 6-12 мес
            min_age_delta = relativedelta(months=6)
            max_age_delta = relativedelta(years=1)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == '1_3': # 1-3 года
            min_age_delta = relativedelta(years=1)
            max_age_delta = relativedelta(years=3)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == '3_7': # 3-7 лет
            min_age_delta = relativedelta(years=3)
            max_age_delta = relativedelta(years=7)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == '7_inf': # Старше 7 лет
            # Животные, рожденные раньше, чем (now - 7 лет)
            # max_birth_date = now - relativedelta(years=7)
            # return queryset.filter(animal__birth_date__isnull=False, animal__birth_date__lte=max_birth_date)
            # ИЛИ (для согласованности с другими)
            max_age_delta = relativedelta(years=7) # Минимальный возраст
            start_date = now - relativedelta(years=100) # Условно очень старые
            end_date = now - max_age_delta
        else:
            return queryset

        return queryset.filter(animal__birth_date__isnull=False, animal__birth_date__gte=start_date, animal__birth_date__lte=end_date)

    def global_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(animal__name__icontains=value)
            ).distinct()
        return queryset