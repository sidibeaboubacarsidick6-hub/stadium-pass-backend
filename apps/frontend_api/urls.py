"""
Stadium Pass — URLs API frontend.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    MatchViewSet,
    TeamViewSet,
    create_order,
    me,
    my_tickets,
    register,
    simulate_payment,
)

router = DefaultRouter()
router.register(r'matches', MatchViewSet, basename='match')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    # Auth
    path('auth/register/', register, name='auth-register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', me, name='auth-me'),

    # Orders
    path('orders/', create_order, name='create-order'),
    path('orders/<uuid:uuid>/simulate-pay/', simulate_payment, name='simulate-payment'),
    path('my-tickets/', my_tickets, name='my-tickets'),

    # Resources
    path('', include(router.urls)),
]