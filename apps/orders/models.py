"""
Stadium Pass — Modèles commandes.
"""
import secrets

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


def generate_order_number():
    """Génère un numéro de commande : ORD-XXXXXX."""
    alphabet = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
    while True:
        suffix = ''.join(secrets.choice(alphabet) for _ in range(6))
        number = f"ORD-{suffix}"
        if not Order.objects.filter(order_number=number).exists():
            return number


class Order(UUIDModel, TimeStampedModel):
    """Une commande passée par un supporter."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente de paiement'
        PAID = 'paid', 'Payée'
        FAILED = 'failed', 'Échouée'
        CANCELLED = 'cancelled', 'Annulée'
        REFUNDED = 'refunded', 'Remboursée'

    order_number = models.CharField(
        "numéro de commande", max_length=20,
        unique=True, default=generate_order_number,
    )

    # Acheteur (peut être un user connecté OU un invité)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='orders',
        help_text="Null si achat sans compte (guest).",
    )
    guest_email = models.EmailField("email invité", blank=True)
    guest_phone = models.CharField("téléphone invité", max_length=20, blank=True)
    guest_first_name = models.CharField("prénom invité", max_length=100, blank=True)
    guest_last_name = models.CharField("nom invité", max_length=100, blank=True)

    # Match concerné
    match = models.ForeignKey(
        'matches.Match', on_delete=models.PROTECT,
        related_name='orders',
    )

    # Montants
    subtotal = models.DecimalField(
        "sous-total", max_digits=10, decimal_places=0, default=0,
    )
    fees = models.DecimalField(
        "frais de service", max_digits=10, decimal_places=0, default=0,
    )
    total = models.DecimalField(
        "total payé", max_digits=10, decimal_places=0, default=0,
    )

    # Statut
    status = models.CharField(
        "statut", max_length=20,
        choices=Status.choices, default=Status.PENDING,
    )
    paid_at = models.DateTimeField("payé le", null=True, blank=True)
    cancelled_at = models.DateTimeField("annulé le", null=True, blank=True)

    # Jeton pour les URLs publiques (guest)
    access_token = models.UUIDField(
        "jeton d'accès", unique=True, editable=False,
        default=__import__('uuid').uuid4, db_index=True,
    )

    class Meta:
        verbose_name = "commande"
        verbose_name_plural = "commandes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f"{self.order_number} — {self.match}"

    @property
    def buyer_email(self):
        if self.buyer:
            return self.buyer.email
        return self.guest_email

    @property
    def buyer_name(self):
        if self.buyer:
            return self.buyer.full_name
        return f"{self.guest_first_name} {self.guest_last_name}".strip()

    def mark_as_paid(self, payment_method='simulated', payment_reference=''):
        """
        Marque la commande payée et génère les billets.
        Idempotent : ne fait rien si déjà PAID.
        """
        from django.db import transaction
        from django.utils import timezone

        with transaction.atomic():
            locked = type(self).objects.select_for_update().get(pk=self.pk)
            if locked.status == self.Status.PAID:
                return False

            locked.status = self.Status.PAID
            locked.paid_at = timezone.now()
            locked.save(update_fields=['status', 'paid_at'])

            for item in locked.items.all():
                item.generate_tickets()

        return True

class OrderItem(TimeStampedModel):
    """Ligne d'une commande (une catégorie de billets + quantité)."""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items',
    )
    category = models.ForeignKey(
        'tickets.TicketCategory', on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveIntegerField("quantité", default=1)
    unit_price = models.DecimalField(
        "prix unitaire", max_digits=10, decimal_places=0,
    )
    subtotal = models.DecimalField(
        "sous-total", max_digits=10, decimal_places=0,
    )

    class Meta:
        verbose_name = "ligne de commande"
        verbose_name_plural = "lignes de commande"

    def __str__(self):
        return f"{self.quantity}x {self.category.name}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        
    def generate_tickets(self):
        """Crée N billets (1 par unité) pour cette ligne de commande."""
        from apps.tickets.models import Ticket

        order = self.order
        category = self.category

        for _ in range(self.quantity):
            Ticket.objects.create(
                category=category,
                order_id=order.pk,
                gate_label=category.gate.name if category.gate else '',
                block_label=category.block_label,
                holder_name=order.buyer_name,
                holder_email=order.buyer_email,
                holder_phone=order.guest_phone or (order.buyer.phone if order.buyer else ''),
            )
