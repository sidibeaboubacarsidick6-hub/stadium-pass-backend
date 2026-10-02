"""Stadium Pass — Serializers commandes (API)."""
from rest_framework import serializers

from apps.orders.models import Order, OrderItem
from apps.tickets.models import TicketCategory


class OrderCreateSerializer(serializers.Serializer):
    match_uuid = serializers.UUIDField()
    category_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=10)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['wave', 'orange', 'mtn', 'moov', 'card'],
        default='wave',
    )

    def validate(self, data):
        try:
            category = TicketCategory.objects.select_related(
                'match'
            ).get(pk=data['category_id'], is_active=True)
        except TicketCategory.DoesNotExist:
            raise serializers.ValidationError("Catégorie introuvable.")

        if str(category.match.uuid) != str(data['match_uuid']):
            raise serializers.ValidationError("La catégorie n'appartient pas à ce match.")

        if category.is_sold_out:
            raise serializers.ValidationError("Cette catégorie est épuisée.")

        if category.remaining < data['quantity']:
            raise serializers.ValidationError(
                f"Seulement {category.remaining} place(s) disponible(s)."
            )

        data['category'] = category
        data['match'] = category.match
        return data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'uuid', 'order_number', 'status',
            'subtotal', 'fees', 'total',
            'guest_first_name', 'guest_last_name', 'guest_email',
            'created_at',
        ]
