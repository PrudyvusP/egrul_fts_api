from django.utils.translation import gettext_lazy as _
from rest_framework import pagination
from rest_framework.response import Response

from organizations.models import EgrulVersion


class CustomNumberPagination(pagination.PageNumberPagination):
    page_query_description = _('Номер страницы')

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'date_info': (
                EgrulVersion
                .objects
                .values_list('version', flat=True)
                .first()
            ),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'required': '',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 322,
                    'description': 'Общее количество объектов',
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': 'Ссылка на следующую страницу'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'description': 'Ссылка на предыдущую страницу'
                },
                'date_info': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'date',
                    'description': 'Дата актуальности ЕГРЮЛ'
                },
                'results': schema,
            },
        }
