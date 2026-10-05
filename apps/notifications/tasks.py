import logging
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_ticket_confirmation_email(self, order_id):
    from apps.orders.models import Order
    from apps.tickets.utils import generate_ticket_pdf

    try:
        order = Order.objects.select_related("buyer").get(id=order_id)
    except Order.DoesNotExist:
        logger.warning("Order %s introuvable, email annulé", order_id)
        return

    tickets = list(order.items.select_related(
        "category__match__home_team",
        "category__match__away_team",
        "category__match__competition",
        "category__match__venue",
        "category__gate",
    ).all())  # adapte selon ton modèle (OrderItem → Ticket)

    if not tickets:
        logger.warning("Order %s sans tickets, email annulé", order_id)
        return

    # Récupère les Ticket réels
    ticket_objs = [item.ticket for item in tickets if getattr(item, "ticket", None)]
    if not ticket_objs:
        logger.warning("Order %s sans Ticket liés, email annulé", order_id)
        return

    match = ticket_objs[0].category.match
    recipient = order.buyer_email or (order.buyer.email if order.buyer else None)
    if not recipient:
        logger.warning("Order %s sans email destinataire", order_id)
        return

    # Contexte templates
    ctx = {
        "order": order,
        "tickets": ticket_objs,
        "match": match,
        "frontend_url": getattr(settings, "FRONTEND_URL", "http://localhost:5173"),
    }

    subject = f"🎫 Vos billets Stadium Pass — {match.home_team.short_name} vs {match.away_team.short_name}"
    text_body = render_to_string("emails/ticket_confirmation.txt", ctx)
    html_body = render_to_string("emails/ticket_confirmation.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_body, "text/html")

    # --- Pièces jointes : PDF + QR inline ---
    for ticket in ticket_objs:
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
                with ticket.qr_code_image.open("rb") as f:
                    from email.mime.image import MIMEImage
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

    try:
        msg.send(fail_silently=False)
        logger.info("Email confirmation envoyé pour order %s → %s", order_id, recipient)
    except Exception as exc:
        logger.exception("Échec envoi email order %s", order_id)
        raise self.retry(exc=exc)