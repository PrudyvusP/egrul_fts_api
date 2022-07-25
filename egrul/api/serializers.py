from django.urls import reverse
from rest_framework import serializers

from organizations.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """Сериализатор для организации."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ('full_name', 'short_name', 'inn', 'url')

    def get_url(self, obj):
        return reverse('api:organization-detail', kwargs={'pk': obj.id})
