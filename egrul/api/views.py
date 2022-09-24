from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .mixins import RetrieveListViewSet
from .serializers import (OrganizationListSerializer,
                          OrganizationRetrieveSerializer)
from organizations.models import Organization


def response_with_paginator(viewset, queryset):
    """Реализация пагинатора."""

    page = viewset.paginate_queryset(queryset)
    if page:
        serializer = viewset.get_serializer(page, many=True)
        return viewset.get_paginated_response(serializer.data)
    return Response(viewset.get_serializer(queryset, many=True).data)


class OrganizationViewSet(RetrieveListViewSet):
    """Вью-сет для организаций."""

    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ('=inn', '=ogrn')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrganizationRetrieveSerializer
        return OrganizationListSerializer

    @action(detail=False, url_path='fts-search', )
    def organization_list(self, request):
        """Список организаций по параметру q."""

        q = request.GET.get("q")
        if q:
            query = SearchQuery(q, config='russian')
            rank = SearchRank(F('full_name_search'), query)
            orgs = (Organization.objects.annotate(rank=rank)
                    .filter(full_name_search=query)
                    .order_by('-rank', 'full_name')
                    )
            return response_with_paginator(self, orgs)
        return Response({'detail': 'Необходимо передать параметр q'})
