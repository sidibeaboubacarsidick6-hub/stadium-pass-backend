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
            .prefetch_related("ticket_categories")
            .order_by("-kickoff_at")
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return OrganizerMatchWriteSerializer
        return OrganizerMatchSerializer

    def create(self, request, *args, **kwargs):
        from rest_framework import status as http_status
        from rest_framework.response import Response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        match = serializer.save()
        read_serializer = OrganizerMatchSerializer(match, context={"request": request})
        return Response(read_serializer.data, status=http_status.HTTP_201_CREATED)