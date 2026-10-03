"""
Stadium Pass — Modèles billets et QR codes.
"""
import secrets
import uuid as uuid_lib

from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class TicketCategory(TimeStampedModel):
    """Une catégorie de places pour un match (Populaire, Tribune, VIP)."""

    match = models.ForeignKey(
        'matches.Match', on_delete=models.CASCADE,
        related_name='ticket_categories',
    )
    name = models.CharField(
        "nom", max_length=100,
        help_text="Ex : Populaire, Tribune, VIP, Loge...",
    )
    description = models.TextField("description", blank=True)
    price = models.DecimalField(
        "prix (FCFA)", max_digits=10, decimal_places=0,
    )
    total_quantity = models.PositiveIntegerField(
        "quantité totale",
        help_text="Nombre de places disponibles dans cette catégorie.",
    )
    quantity_sold = models.PositiveIntegerField(
        "vendues", default=0, editable=False,
    )
    max_per_order = models.PositiveIntegerField(
        "max par commande", default=10,
    )
    gate = models.ForeignKey(
        'venues.Gate', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='ticket_categories',
        verbose_name="porte d'accès",
    )
    block_label = models.CharField(
        "bloc / tribune", max_length=50, blank=True,
        help_text="Ex : Bloc 12, Tribune Sud...",
    )
    order = models.PositiveIntegerField("ordre d'affichage", default=0)
    is_active = models.BooleanField("active", default=True)

    class Meta:
        verbose_name = "catégorie de billets"
        verbose_name_plural = "catégories de billets"
        ordering = ['match', 'order', 'price']
        constraints = [
            models.UniqueConstraint(
                fields=['match', 'name'],
                name='unique_category_per_match',
            ),
        ]

    def __str__(self):
        return f"{self.match} — {self.name} ({self.price} FCFA)"

    @property
    def remaining(self):
        return max(0, self.total_quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        return self.remaining == 0

    @property
    def sold_percent(self):
        if self.total_quantity == 0:
            return 0
        return round((self.quantity_sold / self.total_quantity) * 100, 1)


def generate_ticket_number():
    """Génère un numéro de billet unique : TK-XXXX-XXXX."""
    alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    while True:
        part1 = ''.join(secrets.choice(alphabet) for _ in range(4))
        part2 = ''.join(secrets.choice(alphabet) for _ in range(4))
        number = f"TK-{part1}-{part2}"
        if not Ticket.objects.filter(ticket_number=number).exists():
            return number


class Ticket(UUIDModel, TimeStampedModel):
    """
    Un billet individuel.

    1 billet = 1 personne = 1 QR code unique.
    Pour un billet famille de 4, on crée 4 Ticket distincts.
    """

    class Status(models.TextChoices):
        VALID = 'valid', 'Valide'
        USED = 'used', 'Utilisé'
        CANCELLED = 'cancelled', 'Annulé'
        REFUNDED = 'refunded', 'Remboursé'

    ticket_number = models.CharField(
        "numéro de billet", max_length=20,
        unique=True, default=generate_ticket_number,
    )
    category = models.ForeignKey(
        TicketCategory, on_delete=models.PROTECT,
        related_name='tickets',
    )
    # order = FK vers orders.Order (ajouté plus tard)
    order_id = models.PositiveBigIntegerField(
        null=True, blank=True, db_index=True,
        help_text="ID de la commande (ajouté quand orders existera).",
    )

    # Attributs (copiés au moment de la vente pour l'historique)
    gate_label = models.CharField(
        "porte", max_length=50, blank=True,
    )
    block_label = models.CharField(
        "bloc", max_length=50, blank=True,
    )
    row_label = models.CharField(
        "rangée", max_length=20, blank=True,
    )
    seat_label = models.CharField(
        "siège", max_length=20, blank=True,
    )

    # Porteur (optionnel — pour les billets nominatifs)
    holder_name = models.CharField(
        "nom du porteur", max_length=200, blank=True,
    )
    holder_email = models.EmailField(
        "email du porteur", blank=True,
    )
    holder_phone = models.CharField(
        "téléphone du porteur", max_length=20, blank=True,
    )

    # QR code (signé)
    qr_token = models.UUIDField(
        "jeton QR", default=uuid_lib.uuid4,
        unique=True, editable=False, db_index=True,
    )

    # Statut
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.VALID,
    )

    # Scan
    first_scanned_at = models.DateTimeField(
        "premier scan", null=True, blank=True,
    )
    scanned_count = models.PositiveIntegerField(
        "nombre de scans", default=0,
    )

    class Meta:
        verbose_name = "billet"
        verbose_name_plural = "billets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ticket_number']),
            models.Index(fields=['status', 'category']),
        ]

    def __str__(self):
        return f"{self.ticket_number} — {self.category.name}"

    @property
    def match(self):
        return self.category.match

    @property
    def qr_data(self):
        """
        Payload encodé dans le QR code.
        Format : STADIUM:<qr_token>
        """
        return f"STADIUM:{self.qr_token}"
