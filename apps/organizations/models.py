"""
Stadium Pass — Modèles organisations (organisateurs de compétitions).
"""
import secrets

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


def generate_slug():
    """Génère un slug unique pour l'organisation."""
    alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
    while True:
        suffix = "".join(secrets.choice(alphabet) for _ in range(6))
        if not Organization.objects.filter(slug=suffix).exists():
            return suffix


class Organization(UUIDModel, TimeStampedModel):
    """Une organisation (club, ligue, promoteur) qui gère des compétitions."""

    name = models.CharField("nom", max_length=200)
    slug = models.SlugField(
        "slug", max_length=20, unique=True,
        default=generate_slug, editable=False,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations",
        help_text="Utilisateur responsable principal de l'organisation.",
    )

    # Infos pratiques
    email = models.EmailField("email de contact", blank=True)
    phone = models.CharField("téléphone", max_length=30, blank=True)
    address = models.CharField("adresse", max_length=255, blank=True)
    city = models.CharField("ville", max_length=100, blank=True)
    logo_url = models.URLField("URL du logo", blank=True)
    description = models.TextField("description", blank=True)

    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "organisation"
        verbose_name_plural = "organisations"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["owner", "is_active"]),
        ]

    def __str__(self):
        return self.name
