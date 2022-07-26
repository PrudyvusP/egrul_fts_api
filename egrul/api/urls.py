from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet

app_name = 'api'
router = DefaultRouter()
router.register('organizations', OrganizationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
