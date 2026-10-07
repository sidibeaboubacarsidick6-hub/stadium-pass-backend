"""Seed les sports de base + assigne Football aux Match/Team existants."""
from django.core.management.base import BaseCommand

from apps.sports.models import Sport


SPORTS = [
    {"name": "Football",   "kind": Sport.Kind.TEAM,   "display_order": 10,
     "rules": {"has_draw": True, "periods": 2, "period_duration_min": 45}},
    {"name": "Basketball", "kind": Sport.Kind.TEAM,   "display_order": 20,
     "rules": {"has_draw": False, "periods": 4, "period_duration_min": 10}},
    {"name": "Handball",   "kind": Sport.Kind.TEAM,   "display_order": 30,
     "rules": {"has_draw": True, "periods": 2, "period_duration_min": 30}},
    {"name": "Volleyball", "kind": Sport.Kind.TEAM,   "display_order": 40,
     "rules": {"has_draw": False, "sets_to_win": 3}},
    {"name": "Rugby",      "kind": Sport.Kind.TEAM,   "display_order": 50,
     "rules": {"has_draw": True, "periods": 2, "period_duration_min": 40}},
    {"name": "Combat",     "kind": Sport.Kind.COMBAT, "display_order": 60,
     "rules": {"is_event_night": True}},
]


class Command(BaseCommand):
    help = "Crée les sports de base + assigne Football aux Match/Team existants (idempotent)."

    def handle(self, *args, **options):
        created = 0
        for s in SPORTS:
            obj, was_created = Sport.objects.get_or_create(
                name=s["name"],
                defaults={
                    "kind": s["kind"],
                    "display_order": s["display_order"],
                    "rules": s["rules"],
                },
            )
            if was_created:
                created += 1
                self.stdout.write(f"  + {obj.name} ({obj.kind})")
            else:
                self.stdout.write(f"  = {obj.name} (existe déjà)")

        # Assignation Football aux Match/Team sans sport
        from apps.matches.models import Match
        from apps.teams.models import Team

        football = Sport.objects.filter(name="Football").first()
        if football:
            m_count = Match.objects.filter(sport__isnull=True).update(sport=football)
            t_count = Team.objects.filter(sport__isnull=True).update(sport=football)
            self.stdout.write(f"\n  → {m_count} match(s) assigné(s) à Football")
            self.stdout.write(f"  → {t_count} équipe(s) assignée(s) à Football")

        self.stdout.write(self.style.SUCCESS(f"\n{created} sport(s) créé(s)."))
