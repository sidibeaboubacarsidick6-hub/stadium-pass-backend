"""
Stadium Pass — Script de seed.

Remplit la base avec des données de test réalistes :
- 1 compétition (Championnat de Côte d'Ivoire)
- 1 saison 2026-2027
- 5 journées
- 5 équipes
- 3 stades
- 3 matchs
- 3 catégories de billets par match
- 1 wallet par équipe

Usage :
    python manage.py seed_stadium           # Créer les données (idempotent)
    python manage.py seed_stadium --reset   # Supprimer puis recréer
"""
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.competitions.models import Competition, MatchDay, Season
from apps.matches.models import Match
from apps.teams.models import Team
from apps.tickets.models import TicketCategory
from apps.venues.models import Gate, Venue
from apps.wallet.models import TeamWallet


class Command(BaseCommand):
    help = "Remplit la base avec des données de test Stadium Pass."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help="Supprime les données existantes avant de recréer.",
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING("🗑️  Suppression des données..."))
            Match.objects.all().delete()
            TicketCategory.objects.all().delete()
            TeamWallet.objects.all().delete()
            Team.objects.all().delete()
            Gate.objects.all().delete()
            Venue.objects.all().delete()
            MatchDay.objects.all().delete()
            Season.objects.all().delete()
            Competition.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Données supprimées.\n"))

        # 1. Compétition
        comp, created = Competition.objects.get_or_create(
            name="Championnat de Côte d'Ivoire",
            defaults={
                'type': Competition.Type.CHAMPIONSHIP,
                'description': "Championnat national de football — Ligue 1",
            },
        )
        self.stdout.write(f"{'✅ Créé' if created else '⏭️  Existant'} : {comp.name}")

        # 2. Saison
        season, created = Season.objects.get_or_create(
            competition=comp,
            name="2026-2027",
            defaults={
                'start_date': date(2026, 9, 1),
                'end_date': date(2027, 6, 30),
                'is_current': True,
            },
        )
        self.stdout.write(f"{'✅ Créée' if created else '⏭️  Existante'} : Saison {season.name}")

        # 3. Journées
        for n in range(1, 6):
            md, created = MatchDay.objects.get_or_create(
                season=season, number=n,
                defaults={
                    'name': f"Journée {n}",
                    'start_date': date(2026, 9, 1) + timedelta(days=7 * (n - 1)),
                    'end_date': date(2026, 9, 1) + timedelta(days=7 * (n - 1) + 2),
                },
            )
        self.stdout.write(f"✅ 5 journées créées ou existantes")

        # 4. Stades
        stades_data = [
            {
                'name': "Stade Félix Houphouët-Boigny",
                'city': 'Abidjan',
                'address': 'Plateau, Abidjan',
                'capacity': 35000,
                'gates': [
                    ('Porte A', 'A', 'Virage Nord'),
                    ('Porte B', 'B', 'Virage Sud'),
                    ('Porte C', 'C', 'Tribune Ouest'),
                    ('Porte VIP', 'VIP', 'Loges'),
                ],
            },
            {
                'name': 'Stade Robert Champroux',
                'city': 'Abidjan',
                'address': 'Marcory, Abidjan',
                'capacity': 10000,
                'gates': [
                    ('Porte Principale', 'P', 'Est'),
                    ('Porte Secondaire', 'S', 'Ouest'),
                ],
            },
            {
                'name': 'Stade Municipal de San Pédro',
                'city': 'San Pédro',
                'address': 'Centre-ville, San Pédro',
                'capacity': 5000,
                'gates': [
                    ('Entrée Unique', 'U', 'Principale'),
                ],
            },
        ]

        venues = {}
        for data in stades_data:
            gates_data = data.pop('gates')
            venue, created = Venue.objects.get_or_create(
                name=data['name'],
                defaults=data,
            )
            venues[venue.name] = venue
            for gate_name, gate_code, gate_zone in gates_data:
                Gate.objects.get_or_create(
                    venue=venue, code=gate_code,
                    defaults={
                        'name': gate_name,
                        'zone': gate_zone,
                    },
                )
            self.stdout.write(f"{'✅ Créé' if created else '⏭️  Existant'} : {venue.name}")

        # 5. Équipes
        equipes_data = [
            ('ASEC Mimosas', 'ASEC', 'Abidjan', 1948),
            ('Africa Sports', 'AFR', 'Abidjan', 1948),
            ('Stella Club', 'STE', 'Abidjan', 1953),
            ('SOA', 'SOA', 'Yamoussoukro', 1959),
            ('FC San Pédro', 'FCSP', 'San Pédro', 2000),
        ]
        teams = {}
        for name, short, city, year in equipes_data:
            team, created = Team.objects.get_or_create(
                name=name,
                defaults={
                    'short_name': short,
                    'city': city,
                    'founded_year': year,
                },
            )
            teams[team.short_name] = team
            # Wallet automatique
            TeamWallet.objects.get_or_create(team=team)
            self.stdout.write(f"{'✅ Créée' if created else '⏭️  Existante'} : {team.name}")

        # 6. Matchs
        now = timezone.now()
        matchs_data = [
            {
                'competition': comp,
                'season': season,
                'match_day': MatchDay.objects.get(season=season, number=1),
                'home_team': teams['ASEC'],
                'away_team': teams['AFR'],
                'venue': venues['Stade Félix Houphouët-Boigny'],
                'kickoff_at': now + timedelta(days=7),
                'status': Match.Status.ON_SALE,
                'tv_channel': 'RTI 1',
                'description': "Le derby d'Abidjan — la grande affiche de la journée.",
            },
            {
                'competition': comp,
                'season': season,
                'match_day': MatchDay.objects.get(season=season, number=1),
                'home_team': teams['STE'],
                'away_team': teams['SOA'],
                'venue': venues['Stade Robert Champroux'],
                'kickoff_at': now + timedelta(days=8),
                'status': Match.Status.ON_SALE,
                'description': "Choc du championnat — Stella contre SOA.",
            },
            {
                'competition': comp,
                'season': season,
                'match_day': MatchDay.objects.get(season=season, number=2),
                'home_team': teams['FCSP'],
                'away_team': teams['ASEC'],
                'venue': venues['Stade Municipal de San Pédro'],
                'kickoff_at': now + timedelta(days=15),
                'status': Match.Status.ON_SALE,
                'description': "Le champion en visite à San Pédro.",
            },
        ]

        for data in matchs_data:
            match, created = Match.objects.get_or_create(
                competition=data['competition'],
                home_team=data['home_team'],
                away_team=data['away_team'],
                kickoff_at=data['kickoff_at'],
                defaults=data,
            )
            self.stdout.write(f"{'✅ Créé' if created else '⏭️  Existant'} : {match}")

            # 7. Catégories de billets
            categories = [
                ('Populaire', Decimal('1000'), 25000, 'A', 'Virage Nord'),
                ('Tribune', Decimal('2500'), 8000, 'C', 'Tribune Ouest'),
                ('VIP', Decimal('10000'), 500, 'VIP', 'Loges'),
            ]
            for cat_name, price, qty, gate_code, block in categories:
                cat, cat_created = TicketCategory.objects.get_or_create(
                    match=match, name=cat_name,
                    defaults={
                        'price': price,
                        'total_quantity': qty,
                        'gate': match.venue.gates.filter(code=gate_code).first(),
                        'block_label': block,
                        'order': categories.index((cat_name, price, qty, gate_code, block)),
                    },
                )

        # Résumé
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("🌱 SEED TERMINÉ"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"  Compétitions : {Competition.objects.count()}")
        self.stdout.write(f"  Saisons      : {Season.objects.count()}")
        self.stdout.write(f"  Journées     : {MatchDay.objects.count()}")
        self.stdout.write(f"  Stades       : {Venue.objects.count()}")
        self.stdout.write(f"  Portes       : {Gate.objects.count()}")
        self.stdout.write(f"  Équipes      : {Team.objects.count()}")
        self.stdout.write(f"  Wallets      : {TeamWallet.objects.count()}")
        self.stdout.write(f"  Matchs       : {Match.objects.count()}")
        self.stdout.write(f"  Catégories   : {TicketCategory.objects.count()}")
        self.stdout.write(self.style.SUCCESS("=" * 60))
