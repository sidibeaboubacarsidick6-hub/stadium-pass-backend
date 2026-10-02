"""
Stadium Pass — Modèles comptes utilisateurs.

Un seul modèle User avec un rôle. Les profils sont optionnels
(SupporterProfile pour les supporters, StaffProfile pour le personnel).
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedModel, UUIDModel


class UserManager(BaseUserManager):
    """Manager custom : email comme identifiant unique."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, UUIDModel):
    """Utilisateur de la plateforme (tous rôles confondus)."""

    class Role(models.TextChoices):
        SUPPORTER = 'supporter', 'Supporter'
        TEAM_STAFF = 'team_staff', 'Personnel équipe'
        ORG_STAFF = 'org_staff', 'Personnel organisation'
        SCANNER = 'scanner', 'Agent scanner'
        ADMIN = 'admin', 'Administrateur plateforme'

    email = models.EmailField("email", unique=True)
    first_name = models.CharField("prénom", max_length=100)
    last_name = models.CharField("nom", max_length=100)
    phone = models.CharField(
        "téléphone", max_length=20, blank=True,
        help_text="Format international : +225XXXXXXXXXX",
    )
    role = models.CharField(
        "rôle", max_length=20,
        choices=Role.choices, default=Role.SUPPORTER,
    )
    is_active = models.BooleanField("actif", default=True)
    is_staff = models.BooleanField("accès admin", default=False)
    date_joined = models.DateTimeField("inscrit le", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # Raccourcis pour les templates / permissions
    @property
    def is_supporter(self):
        return self.role == self.Role.SUPPORTER

    @property
    def is_team_staff(self):
        return self.role == self.Role.TEAM_STAFF

    @property
    def is_org_staff(self):
        return self.role == self.Role.ORG_STAFF

    @property
    def is_scanner(self):
        return self.role == self.Role.SCANNER


class SupporterProfile(TimeStampedModel):
    """Profil étendu d'un supporter (infos optionnelles)."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='supporter_profile',
    )
    # favorite_team = FK vers teams.Team → on l'ajoutera quand teams existera
    favorite_team_id = models.PositiveBigIntegerField(
        null=True, blank=True,
        help_text="ID de l'équipe favorite (ajouté plus tard).",
    )
    city = models.CharField("ville", max_length=100, blank=True)
    birth_date = models.DateField("date de naissance", null=True, blank=True)
    accepts_marketing = models.BooleanField("accepte les promos", default=False)

    class Meta:
        verbose_name = "profil supporter"
        verbose_name_plural = "profils supporters"

    def __str__(self):
        return f"Profil de {self.user.full_name}"


class StaffProfile(TimeStampedModel):
    """Profil du personnel rattaché à une équipe ou une organisation."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    # team_id / organization_id → ajoutés quand ces apps existeront
    team_id = models.PositiveBigIntegerField(
        null=True, blank=True,
        help_text="ID de l'équipe (si role=team_staff).",
    )
    organization_id = models.PositiveBigIntegerField(
        null=True, blank=True,
        help_text="ID de l'organisation (si role=org_staff).",
    )
    position = models.CharField("poste", max_length=100, blank=True)
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "profil personnel"
        verbose_name_plural = "profils personnel"

    def __str__(self):
        return f"Staff de {self.user.full_name}"
