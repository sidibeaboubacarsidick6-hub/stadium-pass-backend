"""
Stadium Pass — Modèles statistiques (snapshots).
"""
from django.db import models

from apps.core.models import TimeStampedModel


class MatchStatsSnapshot(TimeStampedModel):
    """
    Snapshot quotidien des stats d'un match.
    Utilisé pour tracer les courbes de vente dans le temps.
    """

    match = models.ForeignKey(
        'matches.Match', on_delete=models.CASCADE,
        related_name='stats_snapshots',
    )
    date = models.DateField("date")

    # Ventes du jour
    tickets_sold = models.PositiveIntegerField("billets vendus", default=0)
    revenue = models.DecimalField(
        "revenus (FCFA)", max_digits=14, decimal_places=0, default=0,
    )

    # Scans du jour (si applicable)
    tickets_scanned = models.PositiveIntegerField("billets scannés", default=0)

    class Meta:
        verbose_name = "statistiques match (snapshot)"
        verbose_name_plural = "statistiques match (snapshots)"
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(
                fields=['match', 'date'],
                name='unique_snapshot_per_match_per_day',
            ),
        ]

    def __str__(self):
        return f"{self.match} — {self.date} ({self.tickets_sold} billets)"
