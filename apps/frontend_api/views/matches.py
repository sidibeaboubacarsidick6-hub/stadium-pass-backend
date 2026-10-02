"""
Stadium Pass — Vues API pour le frontend.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.matches.models import Match
from apps.teams.models import Team

from ..serializers import (
    MatchDetailSerializer,
    MatchListSerializer,
    TeamSerializer,
)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """API matchs — lecture seule (public)."""
    queryset = Match.objects.select_related(
        'home_team', 'away_team', 'venue', 'competition'
    ).filter(status__in=['on_sale', 'sold_out', 'closed', 'played'])
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    ordering = ['kickoff_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchListSerializer


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """API équipes — lecture seule (public)."""
    queryset = Team.objects.filter(is_active=True).order_by('name')
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
