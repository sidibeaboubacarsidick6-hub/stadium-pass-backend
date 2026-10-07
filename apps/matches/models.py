"""
Stadium Pass — Modèles matchs de football.
"""
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Match(TimeStampedModel, UUIDModel):
    """Un match entre 2 équipes."""
    sport = models.ForeignKey(
        "sports.Sport",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matches",
        help_text="Sport du match (null pour compat historique).",
    )
    
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="matches",
        help_text="Organisation propriétaire (null = donnée historique).",
    )

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        CONFIGURING = 'configuring', 'En configuration'
        ON_SALE = 'on_sale', 'En vente'
        SOLD_OUT = 'sold_out', 'Complet'
        CLOSED = 'closed', 'Vente fermée'
        CANCELLED = 'cancelled', 'Annulé'
        PLAYED = 'played', 'Joué'

    # Organisation
    competition = models.ForeignKey(
        'competitions.Competition', on_delete=models.PROTECT,
        related_name='matches',
    )
    season = models.ForeignKey(
        'competitions.Season', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='matches',
    )
    match_day = models.ForeignKey(
        'competitions.MatchDay', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='matches',
    )

    # Les 2 équipes
    home_team = models.ForeignKey(
        'teams.Team', on_delete=models.PROTECT,
        related_name='home_matches',
        verbose_name="équipe recevante",
    )
    away_team = models.ForeignKey(
        'teams.Team', on_delete=models.PROTECT,
        related_name='away_matches',
        verbose_name="équipe visiteuse",
    )

    # Lieu et date
    venue = models.ForeignKey(
        'venues.Venue', on_delete=models.PROTECT,
        related_name='matches',
    )
    kickoff_at = models.DateTimeField(
        "coup d'envoi",
        help_text="Date et heure du début du match.",
    )

    # Vente de billets
    sale_start_at = models.DateTimeField(
        "ouverture des ventes",
        null=True, blank=True,
    )
    sale_end_at = models.DateTimeField(
        "fermeture des ventes",
        null=True, blank=True,
    )

    # Quota équipe visiteuse (% de places réservées)
    away_quota_percent = models.PositiveIntegerField(
        "quota équipe visiteuse (%)",
        default=10,
        help_text="Pourcentage de places réservées à l'équipe visiteuse.",
    )

    # Statut
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.DRAFT,
    )

    # Optionnel
    poster = models.ImageField(
        "affiche", upload_to='matches/posters/%Y/%m/',
        null=True, blank=True,
    )
    tv_channel = models.CharField(
        "chaîne TV", max_length=100, blank=True,
    )
    description = models.TextField("description", blank=True)

    class Meta:
        verbose_name = "match"
        verbose_name_plural = "matchs"
        ordering = ['-kickoff_at']
        indexes = [
            models.Index(fields=['status', 'kickoff_at']),
            models.Index(fields=['home_team', 'kickoff_at']),
        ]

    def __str__(self):
        return f"{self.home_team.short_name} vs {self.away_team.short_name} — {self.kickoff_at:%d/%m/%Y}"

    @property
    def title(self):
        return f"{self.home_team.name} vs {self.away_team.name}"

    @property
    def total_capacity(self):
        return sum(cat.total_quantity for cat in self.ticket_categories.all())

    @property
    def total_sold(self):
        return sum(cat.quantity_sold for cat in self.ticket_categories.all())

    @property
    def is_on_sale(self):
        return self.status == self.Status.ON_SALE
