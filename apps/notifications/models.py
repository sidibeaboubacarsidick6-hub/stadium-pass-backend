"""
Stadium Pass — Modèles notifications (emails, SMS).
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class NotificationLog(TimeStampedModel):
    """Historique des notifications envoyées."""

    class Channel(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Notification push'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        SENT = 'sent', 'Envoyée'
        FAILED = 'failed', 'Échouée'

    class Kind(models.TextChoices):
        ORDER_CONFIRMED = 'order_confirmed', 'Commande confirmée'
        TICKETS_READY = 'tickets_ready', 'Billets disponibles'
        MATCH_REMINDER = 'match_reminder', 'Rappel de match'
        PASSWORD_RESET = 'password_reset', 'Réinitialisation mot de passe'
        PAYOUT_REQUESTED = 'payout_requested', 'Reversement demandé'
        PAYOUT_COMPLETED = 'payout_completed', 'Reversement effectué'
        OTHER = 'other', 'Autre'

    channel = models.CharField(
        "canal", max_length=20, choices=Channel.choices,
    )
    kind = models.CharField(
        "type", max_length=30, choices=Kind.choices, default=Kind.OTHER,
    )
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )

    # Destinataire
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications',
    )
    recipient_email = models.EmailField("email destinataire", blank=True)
    recipient_phone = models.CharField("téléphone destinataire", max_length=20, blank=True)

    # Contenu
    subject = models.CharField("sujet", max_length=300, blank=True)
    body_preview = models.CharField(
        "aperçu du message", max_length=500, blank=True,
    )

    # Références optionnelles
    order_id = models.PositiveBigIntegerField(null=True, blank=True)
    payout_id = models.PositiveBigIntegerField(null=True, blank=True)

    # Envoi
    sent_at = models.DateTimeField("envoyé le", null=True, blank=True)
    error_message = models.TextField("erreur", blank=True)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['kind']),
        ]

    def __str__(self):
        return f"{self.get_channel_display()} → {self.recipient_email or self.recipient_phone} [{self.status}]"
