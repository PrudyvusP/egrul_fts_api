from rest_framework import filters


class SearchFilterWithCustomDescription(filters.SearchFilter):
    search_title = 'Поиск'
    search_description = 'Параметр поиска по ИНН, КПП, ОГРН'
