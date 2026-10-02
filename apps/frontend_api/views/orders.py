"""Stadium Pass — Vue création de commande (API)."""
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.models import Order, OrderItem
from apps.tickets.models import TicketCategory

from ..serializers.orders import OrderCreateSerializer, OrderSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def create_order(request):
    """Crée une commande (guest). Paiement à intégrer ensuite."""
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    category = data['category']
    match = data['match']
    quantity = data['quantity']

    with transaction.atomic():
        # Verrouille la catégorie pour éviter la survente
        locked_cat = TicketCategory.objects.select_for_update().get(pk=category.pk)
        if locked_cat.remaining < quantity:
            return Response(
                {'error': 'Stock insuffisant.'},
                status=status.HTTP_409_CONFLICT,
            )

        subtotal = locked_cat.price * quantity

        order = Order.objects.create(
            match=match,
            guest_first_name=data['first_name'],
            guest_last_name=data['last_name'],
            guest_email=data['email'],
            guest_phone=data.get('phone', ''),
            subtotal=subtotal,
            fees=0,
            total=subtotal,
            status=Order.Status.PENDING,
        )
        OrderItem.objects.create(
            order=order,
            category=locked_cat,
            quantity=quantity,
            unit_price=locked_cat.price,
            subtotal=subtotal,
        )
        # Réserve le stock (sera libéré si annulation)
        locked_cat.quantity_sold += quantity
        locked_cat.save(update_fields=['quantity_sold'])

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
