"""
Stadium Pass — Modèles portefeuilles équipes.
"""
from django.db import models

from apps.core.models import TimeStampedModel, UUIDModel


class TeamWallet(TimeStampedModel):
    """
    Portefeuille d'une équipe. Crédité après chaque vente de billets
    à domicile, déduction faite de la commission plateforme.
    """

    team = models.OneToOneField(
        'teams.Team', on_delete=models.CASCADE,
        related_name='wallet',
    )

    # Soldes
    balance_available = models.DecimalField(
        "solde disponible", max_digits=14, decimal_places=0, default=0,
        help_text="Montant disponible pour reversement.",
    )
    balance_pending = models.DecimalField(
        "solde en attente", max_digits=14, decimal_places=0, default=0,
        help_text="Montant réservé pour un reversement en cours.",
    )
    balance_withdrawn = models.DecimalField(
        "total reversé", max_digits=14, decimal_places=0, default=0,
        help_text="Total cumulé des reversements effectués.",
    )

    # Méthode de reversement préférée
    class PayoutMethod(models.TextChoices):
        WAVE = 'wave', 'Wave'
        ORANGE = 'orange', 'Orange Money'
        MTN = 'mtn', 'MTN MoMo'
        MOOV = 'moov', 'Moov Money'

    preferred_payout_method = models.CharField(
        "méthode de reversement préférée", max_length=20,
        choices=PayoutMethod.choices, default=PayoutMethod.WAVE,
    )
    payout_phone = models.CharField(
        "numéro Mobile Money", max_length=20, blank=True,
    )
    payout_name = models.CharField(
        "nom du bénéficiaire", max_length=200, blank=True,
    )

    # État
    is_frozen = models.BooleanField(
        "gelé", default=False,
        help_text="Wallet gelé : aucun reversement accepté.",
    )
    frozen_reason = models.TextField(
        "raison du gel", blank=True,
    )

    class Meta:
        verbose_name = "portefeuille équipe"
        verbose_name_plural = "portefeuilles équipes"

    def __str__(self):
        return f"Wallet {self.team.name} — {self.balance_available} FCFA"

    @property
    def total_balance(self):
        return self.balance_available + self.balance_pending

    def credit(self, amount, description='', reference=''):
        """Crédite le wallet après une vente."""
        self.balance_available += amount
        self.save(update_fields=['balance_available', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=self,
            type=WalletTransaction.Type.CREDIT,
            amount=amount,
            balance_after=self.balance_available,
            description=description,
            reference=reference,
        )

    def reserve(self, amount, description='', reference=''):
        """Réserve un montant pour un reversement en cours."""
        if amount > self.balance_available:
            raise ValueError("Solde insuffisant pour ce reversement.")
        self.balance_available -= amount
        self.balance_pending += amount
        self.save(update_fields=['balance_available', 'balance_pending', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=self,
            type=WalletTransaction.Type.ADJUSTMENT,
            amount=amount,
            balance_after=self.balance_available,
            description=description or 'Montant réservé pour reversement',
            reference=reference,
        )

    def complete_reserved(self, amount, description='', reference=''):
        """Finalise un reversement après confirmation provider."""
        if amount > self.balance_pending:
            raise ValueError("Montant réservé insuffisant.")
        self.balance_pending -= amount
        self.balance_withdrawn += amount
        self.save(update_fields=['balance_withdrawn', 'balance_pending', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=self,
            type=WalletTransaction.Type.DEBIT,
            amount=amount,
            balance_after=self.balance_available,
            description=description or 'Reversement confirmé',
            reference=reference,
        )

    def release_reserved(self, amount, description='', reference=''):
        """Libère un montant réservé après échec."""
        if amount > self.balance_pending:
            raise ValueError("Montant réservé insuffisant.")
        self.balance_pending -= amount
        self.balance_available += amount
        self.save(update_fields=['balance_available', 'balance_pending', 'updated_at'])
        WalletTransaction.objects.create(
            wallet=self,
            type=WalletTransaction.Type.ADJUSTMENT,
            amount=amount,
            balance_after=self.balance_available,
            description=description or 'Montant libéré après échec',
            reference=reference,
        )


class WalletTransaction(TimeStampedModel):
    """Historique des mouvements du wallet."""

    class Type(models.TextChoices):
        CREDIT = 'credit', 'Crédit (vente)'
        DEBIT = 'debit', 'Débit (reversement)'
        ADJUSTMENT = 'adjustment', 'Ajustement manuel'
        REFUND = 'refund', 'Remboursement'

    wallet = models.ForeignKey(
        TeamWallet, on_delete=models.CASCADE,
        related_name='transactions',
    )
    type = models.CharField("type", max_length=20, choices=Type.choices)
    amount = models.DecimalField("montant", max_digits=14, decimal_places=0)
    balance_after = models.DecimalField(
        "solde après", max_digits=14, decimal_places=0,
    )
    description = models.CharField("description", max_length=500, blank=True)
    reference = models.CharField("référence", max_length=200, blank=True)

    class Meta:
        verbose_name = "transaction wallet"
        verbose_name_plural = "transactions wallet"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} — {self.amount} FCFA"
