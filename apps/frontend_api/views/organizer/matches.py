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
    lookup_field = "uuid"

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
        from django.db import IntegrityError
        from rest_framework import status as http_status
        from rest_framework.response import Response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            match = serializer.save()
        except IntegrityError as e:
            return Response(
                {"detail": f"Conflit de données : {e}"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        read_serializer = OrganizerMatchSerializer(match, context={"request": request})
        return Response(read_serializer.data, status=http_status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        from django.db import IntegrityError
        from rest_framework import status as http_status
        from rest_framework.response import Response

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            match = serializer.save()
        except IntegrityError as e:
            return Response(
                {"detail": f"Conflit de données : {e}"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        read_serializer = OrganizerMatchSerializer(match, context={"request": request})
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        from rest_framework import status as http_status
        from rest_framework.response import Response
        from apps.tickets.models import Ticket

        instance = self.get_object()
        if Ticket.objects.filter(category__match=instance).exists():
            return Response(
                {"detail": "Impossible de supprimer : des billets sont déjà vendus."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        instance.delete()
        return Response(status=http_status.HTTP_204_NO_CONTENT)