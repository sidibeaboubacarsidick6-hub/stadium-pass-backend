"""
Stadium Pass — URLs API frontend.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MatchViewSet, TeamViewSet
from .views import MatchViewSet, TeamViewSet, create_order

router = DefaultRouter()
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('orders/', create_order, name='create-order'),
    path('', include(router.urls)),
]
