from django.urls import reverse
from rest_framework import serializers

from organizations.models import Organization


class OrganizationListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка организации."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('full_name', 'short_name', 'inn', 'kpp', 'url')

    def get_url(self, obj):
        return reverse('api:organization-detail', kwargs={'pk': obj.id})


class OrganizationRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля организации."""

    class Meta:
        model = Organization
        exclude = ['full_name_search', 'id', 'date_added']
