from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet

app_name = 'api'
router = DefaultRouter()
router.register('organizations', OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
