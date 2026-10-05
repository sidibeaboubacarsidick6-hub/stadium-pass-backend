"""
Stadium Pass — URLs API frontend.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from apps.frontend_api.views.tickets import TicketPDFView

from rest_framework.routers import DefaultRouter
from apps.frontend_api.views.organizer import (
    OrganizerDashboardView,
    OrganizerMatchViewSet,
    OrganizerCompetitionViewSet,
    OrganizerVenueViewSet,
    OrganizerTeamViewSet,
)
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

# Organizer routes
router.register(r"organizer/matches", OrganizerMatchViewSet, basename="organizer-match")
router.register(r"organizer/competitions", OrganizerCompetitionViewSet, basename="organizer-competition")
router.register(r"organizer/venues", OrganizerVenueViewSet, basename="organizer-venue")
router.register(r"organizer/teams", OrganizerTeamViewSet, basename="organizer-team")

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
    path("tickets/<uuid:ticket_uuid>/pdf/", TicketPDFView.as_view(), name="ticket-pdf"),
    path("organizer/dashboard/", OrganizerDashboardView.as_view(), name="organizer-dashboard"),

]