import django_filters

from organizations.models import Organization


class OrganizationFilter(django_filters.FilterSet):
    """Фильтрация по реквизитам организации."""

    inn = django_filters.CharFilter(label='Фильтрация по ИНН организации',
                                    lookup_expr='exact',
                                    min_length=10,
                                    max_length=12)
    kpp = django_filters.CharFilter(label='Фильтрация по КПП организации',
                                    lookup_expr='exact',
                                    min_length=9,
                                    max_length=9
                                    )
    ogrn = django_filters.CharFilter(label='Фильтрация по ОГРН организации',
                                     lookup_expr='exact',
                                     min_length=13,
                                     max_length=13)
    is_main = django_filters.BooleanFilter(label='Фильтрация по основным '
                                                 'организациям '
                                                 'или по филиалам')

    class Meta:
        model = Organization
        fields = ('inn', 'kpp', 'ogrn', 'is_main')
