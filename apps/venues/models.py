"""
Stadium Pass — Modèles stades et portes d'entrée.
"""
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class Venue(TimeStampedModel, UUIDModel):
    """Un stade ou lieu de match."""

    name = models.CharField("nom", max_length=200)
    address = models.TextField("adresse", blank=True)
    city = models.CharField("ville", max_length=100)
    country = models.CharField("pays", max_length=100, default="Côte d'Ivoire")

    capacity = models.PositiveIntegerField(
        "capacité totale", default=0,
        help_text="0 = non renseigné.",
    )

    latitude = models.DecimalField(
        "latitude", max_digits=9, decimal_places=6,
        null=True, blank=True,
    )
    longitude = models.DecimalField(
        "longitude", max_digits=9, decimal_places=6,
        null=True, blank=True,
    )

    image = models.ImageField(
        "image", upload_to='venues/%Y/%m/',
        null=True, blank=True,
    )

    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "stade"
        verbose_name_plural = "stades"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.city})"


class Gate(TimeStampedModel):
    """Porte d'entrée d'un stade (pour le contrôle d'accès)."""

    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE,
        related_name='gates',
    )
    name = models.CharField(
        "nom", max_length=50,
        help_text="Ex : Porte A, Porte Principale...",
    )
    code = models.CharField(
        "code", max_length=10,
        help_text="Code court utilisé pour l'attribution (ex : A, B, C).",
    )
    zone = models.CharField(
        "zone", max_length=100, blank=True,
        help_text="Ex : Virage Nord, Tribune Sud...",
    )
    capacity_per_hour = models.PositiveIntegerField(
        "débit horaire", default=0,
        help_text="0 = non renseigné.",
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "porte d'entrée"
        verbose_name_plural = "portes d'entrée"
        ordering = ['venue', 'code']
        constraints = [
            models.UniqueConstraint(
                fields=['venue', 'code'],
                name='unique_gate_per_venue',
            ),
        ]

    def __str__(self):
        return f"{self.venue.name} — {self.name}"
