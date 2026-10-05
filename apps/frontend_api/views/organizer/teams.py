from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOrganizer
from apps.teams.models import Team

from ...serializers.organizer import OrganizerTeamSerializer


class OrganizerTeamViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizer]
    serializer_class = OrganizerTeamSerializer

    def get_queryset(self):
        return (
            Team.objects
            .filter(organization=self.request.user.organization)
            .order_by("name")
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
