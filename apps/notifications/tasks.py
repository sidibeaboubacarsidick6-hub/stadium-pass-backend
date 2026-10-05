import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_ticket_confirmation_email(self, order_id):
    from apps.orders.models import Order
    from apps.tickets.models import Ticket
    from apps.tickets.utils import generate_ticket_pdf

    # 1. Récupère la commande
    try:
        order = Order.objects.select_related("buyer").get(id=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s introuvable, email annulé", order_id)
        return

    # 2. Récupère les tickets liés (Ticket.order_id = order.pk)
    tickets = list(
        Ticket.objects
        .filter(order_id=order.pk)
        .select_related(
            "category",
            "category__match",
            "category__match__home_team",
            "category__match__away_team",
            "category__match__competition",
            "category__match__venue",
            "category__gate",
        )
    )

    if not tickets:
        logger.warning("Order %s sans tickets, email annulé", order_id)
        return

    # 3. Destinataire
    recipient = order.buyer_email
    if not recipient:
        logger.warning("Order %s sans email destinataire", order_id)
        return

    match = tickets[0].category.match

    # 4. Rendu des templates
    ctx = {
        "order": order,
        "tickets": tickets,
        "match": match,
        "frontend_url": getattr(settings, "FRONTEND_URL", "http://localhost:5173"),
    }

    home = match.home_team.short_name or match.home_team.name
    away = match.away_team.short_name or match.away_team.name
    subject = f"🎫 Vos billets Stadium Pass — {home} vs {away}"

    text_body = render_to_string("emails/ticket_confirmation.txt", ctx)
    html_body = render_to_string("emails/ticket_confirmation.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_body, "text/html")

    # 5. Pièces jointes : PDF + QR inline
    for ticket in tickets:
        # PDF
        try:
            pdf_bytes = generate_ticket_pdf(ticket)
            msg.attach(
                f"billet-{ticket.ticket_number}.pdf",
                pdf_bytes,
                "application/pdf",
            )
        except Exception as e:
            logger.exception("PDF KO pour %s : %s", ticket.ticket_number, e)

        # QR inline (cid:qr-XXXX)
        if ticket.qr_code_image:
            try:
                from email.mime.image import MIMEImage
                with ticket.qr_code_image.open("rb") as f:
                    img = MIMEImage(f.read())
                img.add_header("Content-ID", f"<qr-{ticket.ticket_number}>")
                img.add_header(
                    "Content-Disposition",
                    "inline",
                    filename=f"qr-{ticket.ticket_number}.png",
                )
                msg.attach(img)
            except Exception as e:
                logger.exception("QR inline KO pour %s : %s", ticket.ticket_number, e)

    # 6. Envoi
    try:
        msg.send(fail_silently=False)
        logger.info("Email confirmation envoyé pour %s → %s", order.order_number, recipient)
    except Exception as exc:
        logger.exception("Échec envoi email %s", order.order_number)
        raise self.retry(exc=exc)
