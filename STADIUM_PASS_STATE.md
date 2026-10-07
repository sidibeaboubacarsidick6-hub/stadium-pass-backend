# ⚽ STADIUM PASS — État du projet

**Dernière mise à jour :** 2026-10-07
**Concept :** Billetterie football (Côte d'Ivoire) — test v0 avant intégration IvoirPass Sport

## 🔗 Repos GitHub
- Frontend : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-frontend (commit f3ae408)
- Backend  : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-backend  (commit 24307a0)

## 📁 Chemins locaux
- Frontend : ~/stadium-pass/project/
- Backend  : ~/stadium-pass/backend/

## 🎯 Stack
- Frontend : React + Vite + TS + Tailwind + shadcn + Framer Motion
- Backend  : Django 4.2 + DRF + JWT + SQLite (dev) + Celery + Redis + ReportLab + qrcode

## ✅ Sprint 1 — TERMINÉ

| Étape | Contenu |
|---|---|
| 1 | Auth JWT (register/login/refresh/me) |
| 2 | Paiement simulé (mark_as_paid + tickets auto) |
| 3 | Mes billets (GET /my-tickets/) |
| 4 | Actions client (PDF, calendrier .ics, imprimer) |
| 5 | PDF billet (ReportLab A5 + endpoint) |
| 6 | QR code réel (qrcode[PIL], vert #0a5c3a) |
| 7 | Email confirmation Celery (HTML + TXT + PDF + QR inline) |

**Fix bug my-tickets** : createOrder envoie le JWT + my_tickets matche buyer OU guest_email.

## ✅ Sprint 2 — Organizer : 6/6 phases

### Phase 1 — Modèle Organization
- `apps/organizations/` : Organization (nom, slug auto, owner FK, contact, branding)
- `apps/accounts/` : is_organizer (bool) + organization (FK)

### Phase 2 — FK organization sur modèles
- `Competition`, `Match`, `Venue`, `Team` : + organization (FK, null)

### Phase 3 — Permission + endpoints CRUD backend
- `apps/accounts/permissions.py` : IsOrganizer
- Endpoints : `/api/v1/organizer/{dashboard,matches,competitions,venues,teams}/`
- Filtre auto par user.organization

### Phase 4 — Layout + Dashboard frontend
- `/organizer` : sidebar + garde route + dashboard KPIs

### Phase 5 — Pages CRUD frontend
- `/organizer/matches` : table + Actions (crayon/poubelle)
- `/organizer/competitions` : table + création inline
- `/organizer/venues` : table + création inline
- `/organizer/teams` : table + création inline

### Phase 6 — Formulaire création/édition match
- `/organizer/matches/new` : formulaire complet
- `/organizer/matches/<uuid>/edit` : édition
- Catégories de billets dynamiques (ajouter/supprimer)
- Backend : TicketCategoryNestedSerializer, create/update transactionnels

### Réglages A/B — Édition + suppression
- Actions crayon/poubelle dans la table
- Confirm natif + DELETE API
- Refus si billets déjà vendus
- `lookup_field = 'uuid'` sur les 4 ViewSets → fix 404

## 🚀 Pour relancer

### Redis
sudo service redis-server start
redis-cli ping   # → PONG

### Backend (terminal 1)
cd ~/stadium-pass/backend
source venv/bin/activate
python manage.py runserver 8000

### Frontend (terminal 2)
cd ~/stadium-pass/project
npm run dev    # → http://localhost:5173/

⚠️ Si Vite démarre sur 5174 : pkill -f vite && npm run dev

## ⚙️ Configuration importante

- CELERY_TASK_ALWAYS_EAGER = True → email synchrone en dev (console Django)
- EMAIL_BACKEND = console → rien n'est réellement envoyé en dev
- FRONTEND_URL = http://localhost:5173
- MEDIA_ROOT = backend/media/
- CORS autorise UNIQUEMENT localhost:5173
- SQLite en dev, Postgres à prévoir en preprod

## 🔑 Comptes de test

| Email | Mdp | Rôle |
|---|---|---|
| sidibeaboubacarsidick6@gmail.com | stadium2026 | Supporter |
| ledix2024@gmail.com | stadium2026 | Organizer (Ligue Test) |
| test@test.ci | test1234 | Non-organizer (pour tester le 403) |

## 📌 Prochaines étapes — Sprint 3

| # | Tâche | Effort |
|---|---|---|
| 1 | Intégration paiement Wave | 2-3 j |
| 2 | Intégration Orange Money | 1-2 j |
| 3 | Upload logos (équipes, compétitions, stades) | 0.5 j |
| 4 | Champs sale_start_at / sale_end_at dans le form | 0.5 j |
| 5 | Déploiement preprod (Postgres + SMTP réel) | 1 j |

## 🎯 Triggers pour reprendre
- « ⚽ Stadium Pass — Wave »
- « ⚽ Stadium Pass — Orange Money »
- « ⚽ Stadium Pass — upload logos »
- « ⚽ Stadium Pass — déploiement »
- « ⚽ Stadium Pass — réglages organizer »