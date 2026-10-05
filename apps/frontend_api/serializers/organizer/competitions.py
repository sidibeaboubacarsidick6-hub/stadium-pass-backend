from rest_framework import serializers

from apps.competitions.models import Competition


class OrganizerCompetitionSerializer(serializers.ModelSerializer):
    matches_count = serializers.IntegerField(source="matches.count", read_only=True)

    class Meta:
        model = Competition
        fields = [
            "id", "uuid", "name", "type",
            "matches_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
