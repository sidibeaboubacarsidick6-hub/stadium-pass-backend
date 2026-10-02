"""
Stadium Pass — Modèles paiements.
"""
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Payment(UUIDModel, TimeStampedModel):
    """Une tentative de paiement pour une commande."""

    class Provider(models.TextChoices):
        WAVE = 'wave', 'Wave'
        ORANGE = 'orange', 'Orange Money'
        MTN = 'mtn', 'MTN MoMo'
        MOOV = 'moov', 'Moov Money'
        CARD = 'card', 'Carte bancaire'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        SUCCESS = 'success', 'Réussi'
        FAILED = 'failed', 'Échoué'
        CANCELLED = 'cancelled', 'Annulé'
        REFUNDED = 'refunded', 'Remboursé'

    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE,
        related_name='payments',
    )
    provider = models.CharField(
        "moyen de paiement", max_length=20,
        choices=Provider.choices,
    )
    amount = models.DecimalField(
        "montant", max_digits=10, decimal_places=0,
    )
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )

    # Références externes (renvoyées par Wave, Orange, etc.)
    provider_reference = models.CharField(
        "référence provider", max_length=200, blank=True,
    )
    provider_token = models.CharField(
        "token provider", max_length=200, blank=True,
    )
    provider_status = models.CharField(
        "statut provider", max_length=50, blank=True,
    )
    last_error = models.TextField("dernière erreur", blank=True)

    # Dates
    initiated_at = models.DateTimeField("initié le", null=True, blank=True)
    completed_at = models.DateTimeField("complété le", null=True, blank=True)

    # Webhook idempotence
    last_webhook_token = models.CharField(
        "dernier token webhook", max_length=200, blank=True,
        help_text="Évite de traiter deux fois le même webhook.",
    )

    class Meta:
        verbose_name = "paiement"
        verbose_name_plural = "paiements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['order', 'status']),
        ]

    def __str__(self):
        return f"{self.get_provider_display()} — {self.amount} FCFA — {self.get_status_display()}"
