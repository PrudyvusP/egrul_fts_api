from django.db.models import Max, Min
from django.utils.translation import gettext_lazy as _
from rest_framework import pagination
from rest_framework.response import Response

from organizations.models import Organization


class CustomNumberPagination(pagination.PageNumberPagination):
    page_query_description = _('Номер страницы')

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
                    'type': 'object',
                    'description': ('Информация о дате и'
                                    ' времени сведений в ЕГРЮЛ'),
                    'properties':
                        {
                            'actual_date': {
                                'type': 'string',
                                'format': 'date-time',
                                'description': ('Дата и время крайней'
                                                ' записи в ЕГРЮЛ')
                            },
                            'from_date': {
                                'type': 'string',
                                'format': 'date-time',
                                'description': ('Дата и время первой'
                                                ' записи в ЕГРЮЛ')
                            }
                    }
                },
                'results': schema,
            },
        }
