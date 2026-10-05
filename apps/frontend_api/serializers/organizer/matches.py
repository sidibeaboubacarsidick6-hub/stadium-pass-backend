from rest_framework import serializers

from apps.matches.models import Match
from apps.teams.models import Team
from apps.venues.models import Venue
from apps.competitions.models import Competition


class OrganizerMatchSerializer(serializers.ModelSerializer):
    """Lecture d'un match (avec libellés)."""
    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    competition_name = serializers.CharField(source="competition.name", read_only=True)
    tickets_sold = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            "id", "uuid",
            "competition", "competition_name",
            "home_team", "home_team_name",
            "away_team", "away_team_name",
            "venue", "venue_name",
            "kickoff_at", "sale_start_at", "sale_end_at",
            "status", "tv_channel", "description",
            "tickets_sold",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def get_tickets_sold(self, obj):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(category__match=obj).count()


class OrganizerMatchWriteSerializer(serializers.ModelSerializer):
    """Écriture d'un match (création/édition)."""
    class Meta:
        model = Match
        fields = [
            "competition", "home_team", "away_team", "venue",
            "kickoff_at", "sale_start_at", "sale_end_at",
            "status", "tv_channel", "description",
        ]

    def validate(self, attrs):
        home = attrs.get("home_team") or getattr(self.instance, "home_team", None)
        away = attrs.get("away_team") or getattr(self.instance, "away_team", None)
        if home and away and home == away:
            raise serializers.ValidationError(
                "L'équipe à domicile et l'équipe à l'extérieur doivent être différentes."
            )
        return attrs
