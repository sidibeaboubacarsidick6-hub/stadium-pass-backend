"""Stadium Pass — Permissions DRF custom."""
from rest_framework.permissions import BasePermission


class IsOrganizer(BasePermission):
    """Autorise uniquement les utilisateurs organisateurs actifs."""

    message = "Vous devez être organisateur pour accéder à cette ressource."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not getattr(user, "is_organizer", False):
            return False
        org = getattr(user, "organization", None)
        if org is None or not org.is_active:
            return False
        return True
