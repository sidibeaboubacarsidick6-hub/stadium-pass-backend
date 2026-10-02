"""
Stadium Pass — Modèles équipes / clubs.
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel, UUIDModel


class Team(TimeStampedModel, UUIDModel):
    """Une équipe / club de football."""

    name = models.CharField("nom complet", max_length=200, unique=True)
    short_name = models.CharField(
        "nom court", max_length=50,
        help_text="Ex : ASEC, Africa Sports, SOA...",
    )
    slug = models.SlugField(
        "slug", max_length=220, unique=True, blank=True,
    )
    city = models.CharField("ville", max_length=100, blank=True)
    logo = models.ImageField(
        "logo", upload_to='teams/logos/%Y/%m/',
        null=True, blank=True,
    )
    founded_year = models.PositiveIntegerField(
        "année de fondation", null=True, blank=True,
    )
    president_name = models.CharField(
        "président", max_length=200, blank=True,
    )
    stadium = models.ForeignKey(
        'venues.Venue', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='home_teams',
        verbose_name="stade domicile",
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "équipe"
        verbose_name_plural = "équipes"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TeamStaff(TimeStampedModel):
    """Personnel rattaché à une équipe."""

    class Role(models.TextChoices):
        MANAGER = 'manager', 'Responsable / Président'
        COACH = 'coach', 'Entraîneur'
        MEDICAL = 'medical', 'Médical'
        COMMUNICATION = 'communication', 'Communication'
        OTHER = 'other', 'Autre'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='team_roles',
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='staff',
    )
    role = models.CharField(
        "rôle", max_length=20,
        choices=Role.choices, default=Role.OTHER,
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "membre du staff"
        verbose_name_plural = "membres du staff"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'team', 'role'],
                name='unique_user_team_role',
            ),
        ]

    def __str__(self):
        return f"{self.user.full_name} — {self.team.name} ({self.get_role_display()})"
