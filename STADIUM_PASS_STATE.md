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