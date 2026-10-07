from rest_framework import serializers

from apps.venues.models import Venue


class OrganizerVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = [
            "id", "uuid",
            "name", "city", "address", "country", "capacity",
            "zone_template",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def validate_zone_template(self, value):
        """Valide la structure JSON."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Doit être une liste.")
        for i, z in enumerate(value):
            if not isinstance(z, dict):
                raise serializers.ValidationError(
                    f"Zone {i + 1} : doit être un objet."
                )
            if not z.get("name", "").strip():
                raise serializers.ValidationError(
                    f"Zone {i + 1} : le nom est requis."
                )
            try:
                cap = int(z.get("capacity", 0))
                price = int(z.get("price_base", 0))
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    f"Zone {i + 1} : capacity et price_base doivent être des nombres."
                )
            if cap <= 0:
                raise serializers.ValidationError(
                    f"Zone {i + 1} : capacity doit être > 0."
                )
            if price < 0:
                raise serializers.ValidationError(
                    f"Zone {i + 1} : price_base doit être >= 0."
                )
        return value