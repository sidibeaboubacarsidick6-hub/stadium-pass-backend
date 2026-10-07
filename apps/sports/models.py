"""
Stadium Pass — Modèle Sport.

Chaque sport porte sa configuration. Le schéma reste générique ;
c'est `kind` + `rules` (JSON) qui différencient les comportements.
"""
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel, UUIDModel


class Sport(UUIDModel, TimeStampedModel):
    """Un sport (football, basketball, combat…)."""

    class Kind(models.TextChoices):
        TEAM = "team", "Sport d'équipe"
        COMBAT = "combat", "Sport de combat"

    name = models.CharField("nom", max_length=80, unique=True)
    slug = models.SlugField("slug", max_length=80, unique=True, blank=True)
    kind = models.CharField(
        "type", max_length=20,
        choices=Kind.choices, default=Kind.TEAM,
    )
    description = models.TextField("description", blank=True)

    # Config libre par sport (ex: {"has_draw": true, "periods": 2})
    rules = models.JSONField(
        "règles / configuration",
        default=dict, blank=True,
    )

    display_order = models.PositiveIntegerField("ordre d'affichage", default=0)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "sport"
        verbose_name_plural = "sports"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        super().save(*args, **kwargs)
