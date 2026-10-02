"""
Stadium Pass — Modèles de base (core).

Classes abstraites réutilisables dans toutes les apps du projet.
"""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """
    Modèle abstrait qui ajoute automatiquement :
    - created_at : date de création
    - updated_at : date de dernière modification
    """
    created_at = models.DateTimeField(
        "créé le",
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        "modifié le",
        auto_now=True,
    )

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Modèle abstrait qui ajoute un champ UUID (unique) pour exposer
    des identifiants publics sécurisés (au lieu des PK auto-incrémentés).
    """
    uuid = models.UUIDField(
        "identifiant public",
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Identifiant public sécurisé (utilisé dans les URLs).",
    )

    class Meta:
        abstract = True