"""Stadium Pass — Vues tickets (PDF)."""
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.tickets.models import Ticket
from apps.tickets.utils import generate_ticket_pdf


class TicketPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ticket_uuid):
        ticket = get_object_or_404(
            Ticket.objects.select_related(
                "category__match__home_team",
                "category__match__away_team",
                "category__match__competition",
                "category__match__venue",
                "category__gate",
            ),
            uuid=ticket_uuid,
        )

        from apps.orders.models import Order
        order = Order.objects.get(pk=ticket.order_id)
        if not request.user.is_staff and order.buyer_id != request.user.id:
            raise Http404

        pdf_bytes = generate_ticket_pdf(ticket)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="billet-{ticket.ticket_number}.pdf"'
        )
        return response
