from rest_framework import serializers

from apps.teams.models import Team


class OrganizerTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id", "uuid",
            "name", "short_name", "slug", "city",
            "founded_year", "president_name",
            "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "slug", "created_at", "updated_at"]
