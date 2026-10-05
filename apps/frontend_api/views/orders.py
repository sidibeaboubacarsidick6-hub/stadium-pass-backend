"""Stadium Pass — Vue création de commande (API)."""
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.models import Order, OrderItem
from apps.tickets.models import TicketCategory

from django.shortcuts import get_object_or_404
from apps.orders.models import Order
from ..serializers.orders import OrderCreateSerializer, OrderSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated


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

        # 🎯 V1 : si l'utilisateur est connecté, on lie la commande à son compte
        buyer = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            match=match,
            buyer=buyer,
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





@api_view(['POST'])
@permission_classes([AllowAny])
def simulate_payment(request, uuid):
    """
    Simule le paiement d'une commande (V1 — en attendant Wave).
    Marque la commande PAID + génère les billets.
    """
    order = get_object_or_404(Order, uuid=uuid)
    if order.status == Order.Status.PAID:
        return Response(OrderSerializer(order).data)
    if order.status != Order.Status.PENDING:
        return Response(
            {'error': f"Impossible de payer une commande {order.status}."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    order.mark_as_paid()
    order.refresh_from_db()
    return Response(OrderSerializer(order).data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_tickets(request):
    """Retourne tous les billets du supporter connecté."""
    from apps.tickets.models import Ticket
    from ..serializers.tickets import TicketSerializer

    # Récupère les IDs des commandes du user
    from django.db.models import Q
    order_ids = (
        Order.objects
        .filter(Q(buyer=request.user) | Q(guest_email=request.user.email))
        .values_list('id', flat=True)
    )

    # Récupère les tickets liés à ces commandes
    tickets = (
        Ticket.objects
        .filter(order_id__in=order_ids)
        .select_related(
            'category',
            'category__match',
            'category__match__home_team',
            'category__match__away_team',
            'category__match__venue',
        )
        .order_by('-created_at')
    )

    return Response(TicketSerializer(tickets, many=True, context={'request': request}).data)