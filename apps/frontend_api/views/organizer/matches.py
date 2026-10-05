from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOrganizer
from apps.matches.models import Match

from ...serializers.organizer import (
    OrganizerMatchSerializer,
    OrganizerMatchWriteSerializer,
)


class OrganizerMatchViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        org = self.request.user.organization
        return (
            Match.objects
            .filter(organization=org)
            .select_related("home_team", "away_team", "venue", "competition")
            .order_by("-kickoff_at")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return OrganizerMatchWriteSerializer
        return OrganizerMatchSerializer

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
