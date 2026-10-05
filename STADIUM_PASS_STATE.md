# ⚽ STADIUM PASS — État du projet

**Dernière mise à jour :** 2026-10-05
**Concept :** Billetterie football (Côte d'Ivoire) — test v0 avant intégration IvoirPass Sport

## 🔗 Repos GitHub
- Frontend : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-frontend (commit 513ae7a)
- Backend  : https://github.com/sidibeaboubacarsidick6-hub/stadium-pass-backend  (commit à venir)

## 📁 Chemins locaux
- Frontend : ~/stadium-pass/project/
- Backend  : ~/stadium-pass/backend/

## 🎯 Stack
- Frontend : React + Vite + TS + Tailwind + shadcn + Framer Motion
- Backend  : Django 4.2 + DRF + JWT + SQLite (dev) + Celery + Redis + ReportLab + qrcode

## ✅ Sprint 1 — TERMINÉ

### Étape 1 — Auth JWT
- simplejwt 5.5.1
- /api/v1/auth/register/ , /login/ , /refresh/ , /me/
- Frontend : src/lib/auth.ts (pub/sub), src/lib/api.ts
- User de test : sidibeaboubacarsidick6@gmail.com / stadium2026 (buyer_id=2)

### Étape 2 — Paiement simulé
- Order.mark_as_paid() (dans la classe Order, PAS au niveau module)
- POST /api/v1/orders/<uuid>/simulate-pay/
- create_order lie buyer=request.user si authentifié

### Étape 3 — Mes billets
- GET /api/v1/my-tickets/ (IsAuthenticated)
- TicketSerializer expose qr_code_image_url

### Étape 4 — Actions client
- src/lib/ticket-adapter.ts : Ticket → props TicketCard
- src/lib/ics.ts : génération .ics (Google/Apple)
- 3 boutons : PDF, Calendrier, Imprimer

### Étape 5 — PDF billet ✅
- Backend : apps/tickets/utils.py → generate_ticket_pdf() (ReportLab A5 paysage)
- Vue : apps/frontend_api/views/tickets.py → TicketPDFView (JWT + owner check)
- URL : GET /api/v1/tickets/<uuid>/pdf/
- Frontend : src/lib/api.ts → downloadTicketPdf() (fetch + Blob)
- src/pages/MyTicketsPage.tsx → handleDownloadPdf réel

### Étape 6 — QR code réel ✅
- apps/tickets/models.py : qr_code_data + qr_code_image (migration 0002)
- apps/tickets/utils.py : generate_qr_image() (qrcode[PIL], vert #0a5c3a)
- MEDIA_URL + MEDIA_ROOT config + static serving en dev

### Étape 7 — Email confirmation ✅
- Celery 5.4.0 + Redis
- config/celery.py + __init__.py
- Celery settings : CELERY_TASK_ALWAYS_EAGER=True en dev (synchrone)
- apps/notifications/tasks.py : send_ticket_confirmation_email
- Templates HTML + TXT : apps/notifications/templates/emails/
- Email : sujet avec emoji, PDF attaché + QR inline (Content-ID)
- mark_as_paid() appelle .delay()

## 🚀 Pour relancer

### Redis (à démarrer une fois)
sudo service redis-server start
redis-cli ping   # → PONG

### Backend (terminal 1)
cd ~/stadium-pass/backend
source venv/bin/activate
python manage.py runserver 8000

### Frontend (terminal 2)
cd ~/stadium-pass/project
npm run dev    # Doit être sur http://localhost:5173/

⚠️ Si Vite démarre sur 5174 : pkill -f vite && npm run dev

### Worker Celery (optionnel en dev, obligatoire en prod)
celery -A config worker -l info

## ⚙️ Configuration importante

- CELERY_TASK_ALWAYS_EAGER = True → email envoyé en synchrone en dev
  (pas besoin de worker, l'email apparaît dans la console Django)
- EMAIL_BACKEND = console → en dev, l'email s'affiche dans le terminal
- FRONTEND_URL = http://localhost:5173
- MEDIA_ROOT = backend/media/
- CORS autorise UNIQUEMENT localhost:5173 (pas 5174)
- SQLite en dev, Postgres à prévoir en preprod

## 🔴 Points d'attention

- Le CORS backend autorise UNIQUEMENT localhost:5173 (pas 5174)
- Le backend utilise SQLite en dev (pas encore Postgres)
- Pas de paiement réel — l'order passe en PAID via simulate-pay/
- L'email en dev utilise le backend console (rien n'est réellement envoyé)
- Pour un vrai envoi : configurer SMTP (Brevo, Sendgrid, Mailgun...)

## 📌 Prochaines étapes — Sprint 2

| # | Tâche | Effort |
|---|---|---|
| 1 | Intégration paiement Wave / Orange Money | 2-3 j |
| 2 | Dashboard club (back-office) | 2-3 j |
| 3 | Dashboard admin MKS | 2-3 j |
| 4 | Déploiement preprod Stadium Pass | 1 j |

## 🎯 Triggers pour reprendre
- « ⚽ Stadium Pass — Wave »
- « ⚽ Stadium Pass — Orange Money »
- « ⚽ Stadium Pass — dashboard »
- « ⚽ Stadium Pass — déploiement »
- « ⚽ Stadium Pass — suite Sprint 2 »