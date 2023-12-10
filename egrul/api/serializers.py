from django.urls import reverse
from rest_framework import serializers

from organizations.models import Organization


class OrganizationListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка организации."""

    relative_addr = serializers.SerializerMethodField(
        label='relative_addr',
        help_text='относительный адрес организации в сервисе')

    class Meta:
        model = Organization
        fields = ('full_name', 'short_name', 'inn', 'kpp', 'relative_addr')
        read_only_fields = ('full_name',)

    def get_relative_addr(self, obj):
        return reverse('api:organization-detail', kwargs={'pk': obj.id})


class OrganizationRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля организации."""

    class Meta:
        model = Organization
        fields = ('full_name', 'short_name', 'inn', 'kpp', 'ogrn',
                  'factual_address', 'region_code')
        read_only_fields = ('full_name', 'factual_address', 'ogrn')
