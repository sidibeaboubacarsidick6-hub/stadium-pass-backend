"""
Stadium Pass — Modèles scan des billets à l'entrée.
"""
from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class ScanSession(TimeStampedModel):
    """
    Une session de scan : un agent + un match + une porte.
    """

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='scan_sessions',
    )
    match = models.ForeignKey(
        'matches.Match', on_delete=models.CASCADE,
        related_name='scan_sessions',
    )
    gate = models.ForeignKey(
        'venues.Gate', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scan_sessions',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Compteurs
    total_scanned = models.PositiveIntegerField("total scannés", default=0)
    total_valid = models.PositiveIntegerField("valides", default=0)
    total_rejected = models.PositiveIntegerField("refusés", default=0)

    class Meta:
        verbose_name = "session de scan"
        verbose_name_plural = "sessions de scan"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['match', 'agent']),
        ]

    def __str__(self):
        gate_str = f" — {self.gate.name}" if self.gate else ""
        return f"Session {self.agent.full_name} — {self.match}{gate_str}"


class ScanLog(TimeStampedModel):
    """
    Enregistrement de chaque tentative de scan.
    """

    class Result(models.TextChoices):
        VALID = 'valid', 'Valide ✅'
        ALREADY_USED = 'already_used', 'Déjà utilisé ❌'
        INVALID_QR = 'invalid_qr', 'QR invalide ⛔'
        WRONG_MATCH = 'wrong_match', 'Mauvais match ⚠️'
        TICKET_CANCELLED = 'ticket_cancelled', 'Billet annulé 🚫'
        NOT_FOUND = 'not_found', 'Billet introuvable 🔍'

    session = models.ForeignKey(
        ScanSession, on_delete=models.CASCADE,
        related_name='logs',
    )
    ticket = models.ForeignKey(
        'tickets.Ticket', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scan_logs',
    )
    qr_token_received = models.CharField(
        "token QR reçu", max_length=200, blank=True,
    )
    result = models.CharField(
        "résultat", max_length=20, choices=Result.choices,
    )
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Idempotence pour les scans offline (PWA)
    client_uuid = models.UUIDField(
        "identifiant client", null=True, blank=True,
        db_index=True,
        help_text="UUID généré côté client pour la sync offline.",
    )

    class Meta:
        verbose_name = "log de scan"
        verbose_name_plural = "logs de scan"
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['session', 'result']),
        ]

    def __str__(self):
        return f"{self.get_result_display()} — {self.scanned_at:%H:%M:%S}"
