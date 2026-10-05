from rest_framework import serializers

from apps.venues.models import Venue


class OrganizerVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            "id", "uuid", "name", "city", "address", "capacity",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
