"""Stadium Pass — Serializers billets (API)."""
from rest_framework import serializers

from apps.tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """Billet complet avec infos match + catégorie + QR."""

    match_title = serializers.SerializerMethodField()
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()
    kickoff_at = serializers.SerializerMethodField()
    venue_name = serializers.SerializerMethodField()
    venue_city = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_price = serializers.CharField(source='category.price', read_only=True)
    qr_data = serializers.CharField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'uuid', 'ticket_number',
            'match_title', 'home_team', 'away_team',
            'kickoff_at', 'venue_name', 'venue_city',
            'category_name', 'category_price',
            'gate_label', 'block_label',
            'holder_name', 'holder_email', 'holder_phone',
            'qr_token', 'qr_data',
            'status', 'created_at',
        ]

    def get_match_title(self, obj):
        m = obj.category.match
        return f"{m.home_team.name} vs {m.away_team.name}"

    def get_home_team(self, obj):
        return obj.category.match.home_team.name

    def get_away_team(self, obj):
        return obj.category.match.away_team.name

    def get_kickoff_at(self, obj):
        return obj.category.match.kickoff_at.isoformat()

    def get_venue_name(self, obj):
        return obj.category.match.venue.name

    def get_venue_city(self, obj):
        return obj.category.match.venue.city
