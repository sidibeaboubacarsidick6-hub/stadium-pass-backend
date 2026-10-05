from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOrganizer
from apps.competitions.models import Competition

from ...serializers.organizer import OrganizerCompetitionSerializer


class OrganizerCompetitionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizer]
    serializer_class = OrganizerCompetitionSerializer

    def get_queryset(self):
        return (
            Competition.objects
            .filter(organization=self.request.user.organization)
            .order_by("name")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
