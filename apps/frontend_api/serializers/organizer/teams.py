from rest_framework import serializers

from apps.teams.models import Team


class OrganizerTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "id", "uuid", "name", "short_name", "city", "logo_url",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
