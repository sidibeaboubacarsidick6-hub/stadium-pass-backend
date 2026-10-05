from rest_framework import serializers

from apps.competitions.models import Competition


class OrganizerCompetitionSerializer(serializers.ModelSerializer):
    matches_count = serializers.IntegerField(source="matches.count", read_only=True)
    type = serializers.CharField(required=False, default="championnat")

    class Meta:
        model = Competition
        fields = [
            "id", "uuid",
            "name", "type", "description", "is_active",
            "matches_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
