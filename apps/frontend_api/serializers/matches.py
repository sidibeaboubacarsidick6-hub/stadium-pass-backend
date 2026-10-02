"""
Stadium Pass — Serializers pour l'API frontend.
"""
from rest_framework import serializers

from apps.competitions.models import Competition
from apps.matches.models import Match
from apps.teams.models import Team
from apps.tickets.models import TicketCategory
from apps.venues.models import Venue


class TeamSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'uuid', 'name', 'short_name', 'city', 'logo_url']

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        return None


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id', 'uuid', 'name', 'city', 'address', 'capacity']


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'uuid', 'name', 'type']


class TicketCategorySerializer(serializers.ModelSerializer):
    remaining = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)
    gate_name = serializers.CharField(source='gate.name', read_only=True, default=None)

    class Meta:
        model = TicketCategory
        fields = [
            'id', 'name', 'description', 'price',
            'total_quantity', 'quantity_sold', 'remaining',
            'is_sold_out', 'gate_name', 'block_label', 'order',
        ]


class MatchListSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    competition = CompetitionSerializer(read_only=True)
    min_price = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'uuid', 'title', 'competition',
            'home_team', 'away_team', 'venue',
            'kickoff_at', 'status', 'is_on_sale',
            'poster', 'tv_channel', 'min_price',
        ]

    def get_min_price(self, obj):
        prices = [c.price for c in obj.ticket_categories.filter(is_active=True)]
        return min(prices) if prices else 0


class MatchDetailSerializer(MatchListSerializer):
    ticket_categories = TicketCategorySerializer(many=True, read_only=True)

    class Meta(MatchListSerializer.Meta):
        fields = MatchListSerializer.Meta.fields + [
            'description', 'ticket_categories', 'away_quota_percent',
        ]
