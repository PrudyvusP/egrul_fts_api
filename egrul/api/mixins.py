from rest_framework import mixins, viewsets


class RetrieveViewSet(mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """Миксин для RETRIEVE-only вьюсета."""
    pass
