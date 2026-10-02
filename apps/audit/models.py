"""
Stadium Pass — Modèles journal d'audit.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """
    Journal d'audit — trace toutes les actions sensibles
    (paiements, reversements, modifications critiques).
    """

    class Action(models.TextChoices):
        # Auth
        LOGIN = 'login', 'Connexion'
        LOGOUT = 'logout', 'Déconnexion'
        # Commandes
        ORDER_CREATED = 'order_created', 'Commande créée'
        ORDER_PAID = 'order_paid', 'Commande payée'
        ORDER_CANCELLED = 'order_cancelled', 'Commande annulée'
        ORDER_REFUNDED = 'order_refunded', 'Commande remboursée'
        # Paiements
        PAYMENT_INITIATED = 'payment_initiated', 'Paiement initié'
        PAYMENT_SUCCESS = 'payment_success', 'Paiement réussi'
        PAYMENT_FAILED = 'payment_failed', 'Paiement échoué'
        # Billets
        TICKET_CREATED = 'ticket_created', 'Billet généré'
        TICKET_SCANNED = 'ticket_scanned', 'Billet scanné'
        # Reversements
        PAYOUT_REQUESTED = 'payout_requested', 'Reversement demandé'
        PAYOUT_COMPLETED = 'payout_completed', 'Reversement effectué'
        PAYOUT_FAILED = 'payout_failed', 'Reversement échoué'
        # Admin
        WALLET_FROZEN = 'wallet_frozen', 'Wallet gelé'
        WALLET_UNFROZEN = 'wallet_unfrozen', 'Wallet dégelé'
        # Autre
        OTHER = 'other', 'Autre'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs',
    )
    action = models.CharField("action", max_length=30, choices=Action.choices)
    description = models.TextField("description")

    # Contexte
    model_name = models.CharField("modèle", max_length=100, blank=True)
    object_id = models.CharField("ID objet", max_length=100, blank=True)
    metadata = models.JSONField("métadonnées", null=True, blank=True)

    ip_address = models.GenericIPAddressField(
        "adresse IP", null=True, blank=True,
    )
    user_agent = models.CharField("user-agent", max_length=300, blank=True)

    class Meta:
        verbose_name = "entrée d'audit"
        verbose_name_plural = "journal d'audit"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} — {self.created_at:%d/%m/%Y %H:%M}"
