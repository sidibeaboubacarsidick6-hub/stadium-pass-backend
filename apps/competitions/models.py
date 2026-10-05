"""
Stadium Pass — Modèles compétitions, saisons, journées.
"""
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel, UUIDModel


class Competition(TimeStampedModel, UUIDModel):
    """Une compétition (championnat, coupe, amical)."""
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="competitions",
        help_text="Organisation propriétaire (null = donnée historique).",
    )

    class Type(models.TextChoices):
        CHAMPIONSHIP = 'championship', 'Championnat'
        CUP = 'cup', 'Coupe'
        FRIENDLY = 'friendly', 'Match amical'

    name = models.CharField("nom", max_length=200, unique=True)
    slug = models.SlugField("slug", max_length=220, unique=True, blank=True)
    type = models.CharField(
        "type", max_length=20,
        choices=Type.choices, default=Type.CHAMPIONSHIP,
    )
    description = models.TextField("description", blank=True)
    logo = models.ImageField(
        "logo", upload_to='competitions/logos/%Y/%m/',
        null=True, blank=True,
    )
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "compétition"
        verbose_name_plural = "compétitions"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Season(TimeStampedModel, UUIDModel):
    """Une saison d'une compétition (ex : 2026-2027)."""

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE,
        related_name='seasons',
    )
    name = models.CharField(
        "nom", max_length=50,
        help_text="Ex : 2026-2027, Édition 2026...",
    )
    start_date = models.DateField("date de début")
    end_date = models.DateField("date de fin")
    is_current = models.BooleanField(
        "saison en cours", default=False,
        help_text="Cocher pour la saison actuellement active.",
    )
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "saison"
        verbose_name_plural = "saisons"
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['competition', 'name'],
                name='unique_season_per_competition',
            ),
        ]

    def __str__(self):
        return f"{self.competition.name} — {self.name}"


class MatchDay(TimeStampedModel):
    """Une journée dans une saison (ex : Journée 5)."""

    season = models.ForeignKey(
        Season, on_delete=models.CASCADE,
        related_name='match_days',
    )
    number = models.PositiveIntegerField("numéro")
    name = models.CharField(
        "nom", max_length=100, blank=True,
        help_text="Optionnel. Si vide, 'Journée N' est utilisé.",
    )
    start_date = models.DateField("date de début", null=True, blank=True)
    end_date = models.DateField("date de fin", null=True, blank=True)

    class Meta:
        verbose_name = "journée"
        verbose_name_plural = "journées"
        ordering = ['season', 'number']
        constraints = [
            models.UniqueConstraint(
                fields=['season', 'number'],
                name='unique_matchday_per_season',
            ),
        ]

    def __str__(self):
        label = self.name or f"Journée {self.number}"
        return f"{self.season.name} — {label}"
