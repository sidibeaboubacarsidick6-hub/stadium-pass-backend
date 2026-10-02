"""
Stadium Pass — Modèles demandes de reversement.
"""
import secrets

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


def generate_payout_reference():
    """Génère une référence : PAY-XXXXXX."""
    alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    while True:
        suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
        ref = f"PAY-{suffix}"
        if not PayoutRequest.objects.filter(reference=ref).exists():
            return ref


class PayoutRequest(UUIDModel, TimeStampedModel):
    """Demande de reversement d'une équipe."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PROCESSING = 'processing', 'En cours'
        COMPLETED = 'completed', 'Réussi'
        FAILED = 'failed', 'Échoué'
        CANCELLED = 'cancelled', 'Annulé'
        REJECTED = 'rejected', 'Rejeté'

    reference = models.CharField(
        "référence", max_length=20,
        unique=True, default=generate_payout_reference,
    )
    wallet = models.ForeignKey(
        'wallet.TeamWallet', on_delete=models.CASCADE,
        related_name='payout_requests',
    )

    # Montant
    amount = models.DecimalField("montant demandé", max_digits=14, decimal_places=0)
    fee = models.DecimalField("frais", max_digits=10, decimal_places=0, default=0)
    amount_net = models.DecimalField(
        "montant net reversé", max_digits=14, decimal_places=0, default=0,
    )

    # Coordonnées de paiement
    class PayoutMethod(models.TextChoices):
        WAVE = 'wave', 'Wave'
        ORANGE = 'orange', 'Orange Money'
        MTN = 'mtn', 'MTN MoMo'
        MOOV = 'moov', 'Moov Money'

    payout_method = models.CharField(
        "méthode", max_length=20, choices=PayoutMethod.choices,
    )
    payout_phone = models.CharField("numéro Mobile Money", max_length=20)
    payout_name = models.CharField("nom bénéficiaire", max_length=200)

    # Statut
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )
    admin_note = models.TextField("note admin", blank=True)

    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='processed_payouts',
    )

    # Traitement provider
    provider = models.CharField("provider", max_length=30, default='paydunya')
    provider_token = models.CharField("token provider", max_length=200, blank=True)
    provider_transaction_id = models.CharField(
        "transaction provider", max_length=200, blank=True,
    )
    provider_status = models.CharField("statut provider", max_length=50, blank=True)
    retry_count = models.PositiveIntegerField("retries", default=0)
    last_error = models.TextField("dernière erreur", blank=True)

    # Dates
    processed_at = models.DateTimeField("traité le", null=True, blank=True)
    completed_at = models.DateTimeField("complété le", null=True, blank=True)

    class Meta:
        verbose_name = "demande de reversement"
        verbose_name_plural = "demandes de reversement"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.reference} — {self.amount} FCFA — {self.get_status_display()}"
