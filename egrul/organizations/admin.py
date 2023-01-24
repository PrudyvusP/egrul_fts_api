from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F

from .models import Organization


@admin.register(Organization)
class OrganizationAdminModel(admin.ModelAdmin):
    """Модель админки для организаций."""

    list_display = ('full_name', 'short_name', 'inn',
                    'ogrn', 'kpp', 'factual_address')
    readonly_fields = ('full_name_search',)
    search_fields = ('inn__exact', 'ogrn__exact')

    def get_queryset(self, request):
        """Переопределяет запрос организаций из БД.
        Скрывает полный список организаций."""

        if request.GET:
            return super().get_queryset(request)
        return Organization.objects.none()

    def get_search_results(self, request, queryset, search_term):
        """Переопределяет реализацию поиска в админке.
        """

        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            int(search_term)
        except ValueError:
            query = SearchQuery(search_term, config='russian')
            rank = SearchRank(F('full_name_search'), query)
            queryset = (self.model.objects
                        .annotate(rank=rank)
                        .filter(full_name_search=query)
                        .order_by('-rank', 'full_name')
                        )
        return queryset, True


admin.site.unregister(User)
admin.site.unregister(Group)
