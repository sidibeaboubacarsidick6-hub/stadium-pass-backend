from rest_framework import serializers

from apps.matches.models import Match
from apps.tickets.models import TicketCategory


class TicketCategoryNestedSerializer(serializers.ModelSerializer):
    """Catégorie imbriquée à la création d'un match (write)."""
    class Meta:
        model = TicketCategory
        fields = [
            "name", "description",
            "price", "total_quantity", "max_per_order",
            "block_label",
        ]


class OrganizerMatchSerializer(serializers.ModelSerializer):
    """Lecture d'un match (avec libellés)."""
    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    competition_name = serializers.CharField(source="competition.name", read_only=True)
    tickets_sold = serializers.SerializerMethodField()
    ticket_categories = serializers.SerializerMethodField()

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
            "ticket_categories",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    def get_tickets_sold(self, obj):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(category__match=obj).count()

    def get_ticket_categories(self, obj):
        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "price": str(c.price),
                "total_quantity": c.total_quantity,
                "quantity_sold": c.quantity_sold,
                "remaining": c.remaining,
                "max_per_order": c.max_per_order,
                "block_label": c.block_label,
            }
            for c in obj.ticket_categories.all().order_by("order")
        ]


class OrganizerMatchWriteSerializer(serializers.ModelSerializer):
    """Écriture d'un match (création avec catégories imbriquées)."""
    ticket_categories = TicketCategoryNestedSerializer(many=True, write_only=True)

    class Meta:
        model = Match
        fields = [
            "competition", "home_team", "away_team", "venue",
            "kickoff_at", "sale_start_at", "sale_end_at",
            "status", "tv_channel", "description",
            "ticket_categories",
        ]

    def validate(self, attrs):
        home = attrs.get("home_team") or getattr(self.instance, "home_team", None)
        away = attrs.get("away_team") or getattr(self.instance, "away_team", None)
        if home and away and home == away:
            raise serializers.ValidationError(
                "L'équipe à domicile et l'équipe à l'extérieur doivent être différentes."
            )
        cats = attrs.get("ticket_categories")
        if cats is not None and len(cats) == 0:
            raise serializers.ValidationError(
                {"ticket_categories": "Au moins une catégorie est requise."}
            )
        return attrs

    def validate_ticket_categories(self, value):
        """Vérifie qu'il n'y a pas de doublon de nom."""
        names = [c["name"].strip().lower() for c in value]
        if len(names) != len(set(names)):
            raise serializers.ValidationError(
                "Chaque catégorie doit avoir un nom unique."
            )
        for c in value:
            if not c["name"].strip():
                raise serializers.ValidationError(
                    "Le nom de catégorie ne peut pas être vide."
                )
            if c["price"] <= 0:
                raise serializers.ValidationError(
                    "Le prix doit être supérieur à 0."
                )
            if c["total_quantity"] <= 0:
                raise serializers.ValidationError(
                    "La quantité doit être supérieure à 0."
                )
        return value

    def create(self, validated_data):
        from django.db import IntegrityError
        from rest_framework import serializers as drf_serializers

        categories_data = validated_data.pop("ticket_categories")
        org = self.context["request"].user.organization
        try:
            match = Match.objects.create(organization=org, **validated_data)
            for i, cat_data in enumerate(categories_data):
                TicketCategory.objects.create(match=match, order=i, **cat_data)
        except IntegrityError as e:
            raise drf_serializers.ValidationError(
                f"Conflit de données : {e}"
            )
        return match

    def update(self, instance, validated_data):
        from django.db import IntegrityError
        from rest_framework import serializers as drf_serializers

        # Sécurité : refus si billets déjà vendus
        from apps.tickets.models import Ticket
        if Ticket.objects.filter(category__match=instance).exists():
            raise drf_serializers.ValidationError(
                "Impossible de modifier ce match : des billets sont déjà vendus."
            )

        categories_data = validated_data.pop("ticket_categories", None)
        try:
            instance = super().update(instance, validated_data)
            if categories_data is not None:
                instance.ticket_categories.all().delete()
                for i, cat_data in enumerate(categories_data):
                    TicketCategory.objects.create(match=instance, order=i, **cat_data)
        except IntegrityError as e:
            raise drf_serializers.ValidationError(f"Conflit de données : {e}")
        return instance