from django.db.models import Sum, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOrganizer
from apps.matches.models import Match
from apps.tickets.models import Ticket


class OrganizerDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizer]

    def get(self, request):
        org = request.user.organization
        matches = Match.objects.filter(organization=org)
        tickets = Ticket.objects.filter(category__match__organization=org)

        total_revenue = (
            Ticket.objects
            .filter(category__match__organization=org)
            .aggregate(total=Sum("category__price"))
            .get("total") or 0
        )

        return Response({
            "organization": {
                "name": org.name,
                "slug": org.slug,
            },
            "matches": {
                "total": matches.count(),
                "upcoming": matches.filter(status="scheduled").count(),
            },
            "tickets": {
                "sold": tickets.count(),
            },
            "revenue": {
                "total": total_revenue,
            },
        })
