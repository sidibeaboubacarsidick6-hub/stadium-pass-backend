from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOrganizer
from apps.venues.models import Venue

from ...serializers.organizer import OrganizerVenueSerializer


class OrganizerVenueViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizer]
    serializer_class = OrganizerVenueSerializer

    def get_queryset(self):
        return (
            Venue.objects
            .filter(organization=self.request.user.organization)
            .order_by("name")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
