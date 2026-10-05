# ⚽ STADIUM PASS — État du projet (à envoyer à Claude)

**Dernière mise à jour :** 2026-10-02 soir
**Concept :** Billetterie football (Côte d'Ivoire) — test v0 avant intégration IvoirPass Sport

## 🔗 Repos GitHub
- Frontend : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-frontend
- Backend  : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-backend

## 📁 Chemins locaux
- Frontend : ~/stadium-pass/project/
- Backend  : ~/stadium-pass/backend/

## 🎯 Stack
- Frontend : React + Vite + TS + Tailwind + shadcn (Bolt) + Framer Motion
- Backend  : Django 4.2 + DRF + SQLite (dev) + Celery + Redis

## ✅ État actuel — v0 fonctionnel

### Backend (17 apps Django)
core, accounts, venues, teams, competitions, matches, tickets,
orders, payments, wallet, payouts, scanner, notifications,
analytics, audit, dashboard, frontend_api

Endpoints API actifs :
- GET /api/v1/matches/            → liste
- GET /api/v1/matches/<uuid>/     → détail
- GET /api/v1/teams/              → équipes
- POST /api/v1/orders/            → créer commande

Seed : python manage.py seed_stadium
(réinitialise avec --reset)

### Frontend
Routes fonctionnelles :
- /              → HomePage (API)
- /matches       → MatchListPage (API)
- /matches/:id   → MatchDetailPage (API)
- /checkout/:uuid → CheckoutFlow v0 (8 fichiers)
- /my-tickets    → TicketCard v0
- /scanner       → ScannerScreen v0

## 🚀 Pour relancer

**Backend (terminal 1) :**
cd ~/stadium-pass/backend
source venv/bin/activate
python manage.py runserver 8000

**Frontend (terminal 2) :**
cd ~/stadium-pass/project
npm run dev    # Doit être sur http://localhost:5173/

⚠️ Si Vite démarre sur 5174, tuer les instances :
pkill -f vite && npm run dev

## 📌 Prochaines étapes

| # | Tâche | Effort |
|---|---|---|
| 1 | Intégration paiement Wave / Orange Money | 2-3 j |
| 2 | Génération QR code + PDF billet | 1 j |
| 3 | Dashboard club (back-office) | 2-3 j |
| 4 | Dashboard admin MKS | 2-3 j |
| 5 | Déploiement preprod Stadium Pass | 1 j |

## 🎯 Triggers pour reprendre
- « ⚽ Stadium Pass — paiement »
- « ⚽ Stadium Pass — QR code »
- « ⚽ Stadium Pass — dashboard »
- « ⚽ Stadium Pass — déploiement »

## 📌 Points d'attention
- Le CORS backend autorise UNIQUEMENT localhost:5173 (pas 5174)
- Le backend utilise SQLite en dev (pas encore Postgres)
- Pas de paiement réel — l'order est créée en PENDING
- CheckoutFlow fait par v0 (composant premium en 8 fichiers)


# ⚽ STADIUM PASS — État au 2026-10-03

## Repos GitHub
- Frontend : stadium-pass-frontend (commit 0479b4b)
- Backend  : stadium-pass-backend  (commit 89d78ee)

## Chemins locaux
- Frontend : ~/stadium-pass/project/
- Backend  : ~/stadium-pass/backend/

## Stack
- Frontend : React + Vite + TS + Tailwind + shadcn + Framer Motion
- Backend  : Django 4.2 + DRF + JWT + SQLite

## ✅ Sprint 1 — Étapes 1-4 faites

### Auth (Étape 1)
- JWT simplejwt 5.5.1
- /api/v1/auth/register/ , /login/ , /refresh/ , /me/
- Frontend : src/lib/auth.ts (pub/sub), src/lib/api.ts
- Header réactif, redirection auto si connecté

### Paiement simulé (Étape 2)
- Order.mark_as_paid() + OrderItem.generate_tickets()
- POST /api/v1/orders/<uuid>/simulate-pay/
- create_order lie buyer=request.user si authentifié

### Mes billets (Étape 3)
- GET /api/v1/my-tickets/
- TicketSerializer (match + catégorie + QR)
- Page MyTicketsPage utilise TicketCard v0

### Actions client (Étape 4)
- src/lib/ticket-adapter.ts : Ticket → props TicketCard
- src/lib/ics.ts : génération .ics (Google/Apple)
- 3 boutons : PDF (stub), Calendrier, Imprimer

## ⏳ Sprint 1 — Étapes 5-7 restantes

### Étape 5 — PDF du billet
- Backend ReportLab (apps/tickets/utils.py)
- Endpoint GET /api/v1/tickets/<uuid>/pdf/
- Style inspiré IvoirPass (même identité visuelle)

### Étape 6 — QR code image réel
- pip install qrcode[pil]
- Propriété Ticket.qr_image (PIL) → base64 ou fichier
- Utiliser dans le PDF + TicketCard

### Étape 7 — Email de confirmation
- Celery + template HTML/TXT
- Envoi après mark_as_paid()

## 🚀 Pour relancer

### Backend
cd ~/stadium-pass/backend
source venv/bin/activate
python manage.py runserver 8000

### Frontend
cd ~/stadium-pass/project
npm run dev

⚠️ CORS autorise UNIQUEMENT localhost:5173

## 🎯 Triggers
- « ⚽ Stadium Pass — PDF billet »
- « ⚽ Stadium Pass — QR code »
- « ⚽ Stadium Pass — email »
- « ⚽ Stadium Pass — suite Sprint 1 »
- « ⚽ Stadium Pass — Wave »