import http

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from organizations.models import Organization
from .filters import SearchFilterWithCustomDescription
from .mixins import RetrieveListViewSet
from .paginators import CustomNumberPagination
from .serializers import (OrganizationListSerializer,
                          OrganizationRetrieveSerializer,
                          ErrorSerializer)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=['Организации'],
        operation_summary="Список организаций",
        operation_description=("Страница доступна всем пользователям. "
                               "Доступен поиск по ИНН, КПП, ОГРН."),
        pagination_class=CustomNumberPagination)
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=['Организации'],
        operation_summary="Получение организации",
        operation_description="Страница доступна всем пользователям.",
        responses={
            '404': openapi.Response('объект не найден',
                                    ErrorSerializer)
        }
    ),
)
class OrganizationViewSet(RetrieveListViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilterWithCustomDescription]
    search_fields = ('=inn', '=ogrn', '=kpp')

    pagination_class = CustomNumberPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrganizationRetrieveSerializer
        return OrganizationListSerializer

    @swagger_auto_schema(
        tags=['Организации'],
        operation_summary='Список организаций по полнотекстовому поиску',
        operation_description=('Страница доступна всем пользователям. Доступен'
                               'полнотекстовый поиск по параметру q.'),
        pagination_class=CustomNumberPagination,
        manual_parameters=[
            openapi.Parameter("q",
                              openapi.IN_QUERY,
                              required=True,
                              description="Параметр полнотекстового поиска",
                              type=openapi.TYPE_STRING)
        ],
        responses={
            '400': openapi.Response('Не передан q', ErrorSerializer)
        }
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
                        data={'detail': 'Необходимо передать параметр q'})
