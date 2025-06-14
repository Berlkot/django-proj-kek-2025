import django_filters
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import Advertisement, Animal, Region, AdStatus, Species, AnimalColor, Breed
from django.db.models import Q


AGE_CHOICES = [
    ("0_0.5", "До 6 месяцев"),
    ("0.5_1", "6-12 месяцев"),
    ("1_3", "1-3 года"),
    ("3_7", "3-7 лет"),
    ("7_inf", "Старше 7 лет"),
    ("unknown", "Возраст неизвестен"),
]


class AdvertisementFilter(django_filters.FilterSet):

    region = django_filters.ModelChoiceFilter(
        field_name="user__region", queryset=Region.objects.all(), label="Регион"
    )

    ad_status = django_filters.ModelChoiceFilter(
        field_name="status", queryset=AdStatus.objects.all(), label="Тип объявления"
    )

    species = django_filters.ModelChoiceFilter(
        field_name="animal__species",
        queryset=Species.objects.all(),
        label="Вид животного",
    )
    gender = django_filters.ChoiceFilter(
        field_name="animal__gender", choices=Animal.GENDER_CHOICES, label="Пол"
    )
    color = django_filters.ModelChoiceFilter(
        field_name="animal__color", queryset=AnimalColor.objects.all(), label="Окрас"
    )

    age_category = django_filters.ChoiceFilter(
        choices=AGE_CHOICES, method="filter_by_age_category", label="Возраст"
    )

    search = django_filters.CharFilter(method="global_search", label="Поиск")

    breed = django_filters.ModelChoiceFilter(
        field_name='animal__breed', 
        queryset=Breed.objects.all(),
        label='Порода'
    )

    publication_date_after = django_filters.DateFilter(
        field_name='publication_date',
        lookup_expr='date__gte',
        label='Опубликовано после (YYYY-MM-DD)'
    )
    publication_date_before = django_filters.DateFilter(
        field_name='publication_date',
        lookup_expr='date__lte',
        label='Опубликовано до (YYYY-MM-DD)'
    )

    class Meta:
        model = Advertisement
        fields = [
            'region', 'ad_status', 'species', 'breed', 'gender', 'color', 
            'age_category', 'search', 'publication_date_after', 'publication_date_before'
        ]

    def filter_by_age_category(self, queryset, name, value):
        now = timezone.now().date()
        if value == "unknown":
            return queryset.filter(animal__birth_date__isnull=True)

        min_age_delta, max_age_delta = None, None

        if value == "0_0.5":
            min_age_delta = relativedelta(months=0)
            max_age_delta = relativedelta(months=6)

            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == "0.5_1":
            min_age_delta = relativedelta(months=6)
            max_age_delta = relativedelta(years=1)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == "1_3":
            min_age_delta = relativedelta(years=1)
            max_age_delta = relativedelta(years=3)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == "3_7":
            min_age_delta = relativedelta(years=3)
            max_age_delta = relativedelta(years=7)
            start_date = now - max_age_delta
            end_date = now - min_age_delta
        elif value == "7_inf":

            max_age_delta = relativedelta(years=7)
            start_date = now - relativedelta(years=100)
            end_date = now - max_age_delta
        else:
            return queryset

        return queryset.filter(
            animal__birth_date__isnull=False,
            animal__birth_date__gte=start_date,
            animal__birth_date__lte=end_date,
        )

    def global_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(description__icontains=value)
                | Q(animal__name__icontains=value)
            ).distinct()
        return queryset
