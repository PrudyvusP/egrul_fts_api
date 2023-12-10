import http

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from organizations.models import Organization
from .filters import OrganizationFilter
from .mixins import RetrieveListViewSet
from .paginators import CustomNumberPagination
from .schemas import DOC_CONSTS
from .serializers import (OrganizationListSerializer,
                          OrganizationRetrieveSerializer)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=DOC_CONSTS["list"]["tags"],
        operation_summary=DOC_CONSTS["list"]["summary"],
        operation_description=DOC_CONSTS["list"]["description"],
        pagination_class=CustomNumberPagination)
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=DOC_CONSTS["retrieve"]["tags"],
        operation_summary=DOC_CONSTS["retrieve"]["summary"],
        operation_description=DOC_CONSTS["retrieve"]["description"],
        responses=DOC_CONSTS["retrieve"]["responses"]
    ),
)
class OrganizationViewSet(RetrieveListViewSet):

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrganizationRetrieveSerializer
        return OrganizationListSerializer

    queryset = (
        Organization
        .objects
        .only('full_name', 'short_name', 'inn', 'kpp', 'ogrn',
              'factual_address', 'region_code')
        .all()
    )

    serializer_class = OrganizationListSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = OrganizationFilter
    pagination_class = CustomNumberPagination

    @swagger_auto_schema(
        name="list-fts",
        tags=DOC_CONSTS["list-fts"]["tags"],
        operation_summary=DOC_CONSTS["list-fts"]["summary"],
        operation_description=DOC_CONSTS["list-fts"]["description"],
        pagination_class=CustomNumberPagination,
        manual_parameters=DOC_CONSTS["list-fts"]["params"],
        responses=DOC_CONSTS["list-fts"]["responses"]
    )
    @action(detail=False, methods=['GET'], url_path='fts-search',
            filter_backends=[])
    def fts_search(self, request):
        """Полнотекстовый поиск организаций по параметру q."""

        q = request.query_params.get('q')
        if q:
            query = SearchQuery(q, config='public.russian_egrul')
            rank = SearchRank(F('full_name_search'), query)
            orgs = (Organization.objects.annotate(rank=rank)
                    .filter(full_name_search=query)
                    .order_by('-rank', 'full_name', 'inn')
                    )
            page = self.paginate_queryset(orgs)
            serializer = self.get_serializer(page, many=True)
            if page:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)

        return Response(status=http.HTTPStatus.BAD_REQUEST,
                        data={'detail': 'Не передан обязательный параметр q.'})
