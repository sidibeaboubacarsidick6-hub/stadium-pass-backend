"""
Stadium Pass — URLs API frontend.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MatchViewSet, TeamViewSet

router = DefaultRouter()
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('', include(router.urls)),
]
