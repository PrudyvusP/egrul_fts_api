from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.db.models import Max, Min
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from .mixins import RetrieveListViewSet
from .serializers import (OrganizationListSerializer,
                          OrganizationRetrieveSerializer)
from organizations.models import Organization


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        date_info = Organization.objects.aggregate(
            actual_date=Max("date_added"),
            from_date=Min("date_added")
        )
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'date_info': date_info,
            'results': data,
        })


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
    search_fields = ('=inn', '=ogrn', '=kpp')

    pagination_class = CustomPagination

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
                    .order_by('-rank', 'full_name', 'inn')
                    )
            return response_with_paginator(self, orgs)
        return Response({'detail': 'Необходимо передать параметр q'})
