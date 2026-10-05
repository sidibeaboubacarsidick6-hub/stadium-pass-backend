"""
Stadium Pass — Utilitaires tickets (QR + PDF).
"""
import io
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def generate_qr_image(ticket):
    """
    Génère l'image QR du billet et la stocke dans ticket.qr_code_image.
    Retourne True si généré, False sinon.
    """
    from django.core.files.base import ContentFile
    import qrcode

    if ticket.qr_code_image:
        return False

    try:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
        )
        qr.add_data(ticket.qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#0a5c3a", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')

        filename = f"{ticket.ticket_number}.png"
        ticket.qr_code_image.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True,
        )
        logger.info(f"QR généré pour {ticket.ticket_number}")
        return True
    except Exception as e:
        logger.exception(f"Erreur génération QR {ticket.ticket_number}: {e}")
        return False


def generate_ticket_pdf(ticket) -> bytes:
    """Génère le PDF du billet (A5 paysage) et retourne les bytes."""
    import os

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A5, landscape
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    GREEN = colors.HexColor("#0a5c3a")
    GREEN_DARK = colors.HexColor("#063d26")
    ORANGE = colors.HexColor("#f97316")
    GREY = colors.HexColor("#6b7280")
    LIGHT = colors.HexColor("#f3f4f6")

    buffer = io.BytesIO()
    page_w, page_h = landscape(A5)
    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))
    c.setTitle(f"Billet {ticket.ticket_number}")

    match = ticket.category.match

    # --- Bandeau haut ---
    c.setFillColor(GREEN)
    c.rect(0, page_h - 22 * mm, page_w, 22 * mm, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(10 * mm, page_h - 12 * mm, "STADIUM PASS")
    c.setFont("Helvetica", 8)
    c.drawString(10 * mm, page_h - 17 * mm, "Billetterie officielle — Côte d'Ivoire")

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(page_w - 10 * mm, page_h - 12 * mm, ticket.ticket_number)

    # --- Compétition ---
    y = page_h - 35 * mm
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10 * mm, y + 6 * mm, (match.competition.name or "").upper())

    # --- Équipes ---
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 20)
    home = match.home_team.short_name or match.home_team.name
    away = match.away_team.short_name or match.away_team.name
    c.drawString(10 * mm, y - 4 * mm, home)
    w_home = c.stringWidth(home, "Helvetica-Bold", 20)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(GREY)
    c.drawString(10 * mm + w_home + 5 * mm, y - 4 * mm, "VS")
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(10 * mm + w_home + 16 * mm, y - 4 * mm, away)

    # --- Infos pratiques ---
    info_y = y - 20 * mm
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(10 * mm, info_y, "DATE")
    c.drawString(55 * mm, info_y, "STADE")
    c.drawString(120 * mm, info_y, "PORTE / BLOC")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(10 * mm, info_y - 5 * mm, match.kickoff_at.strftime("%d/%m/%Y %H:%M"))
    c.drawString(55 * mm, info_y - 5 * mm, match.venue.name)
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(55 * mm, info_y - 9 * mm, match.venue.city)

    gate = ticket.category.gate.name if ticket.category.gate else "—"
    block = ticket.category.block_label or "—"
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(120 * mm, info_y - 5 * mm, gate)
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(120 * mm, info_y - 9 * mm, block)

    # --- Catégorie + prix ---
    band_y = info_y - 22 * mm
    c.setFillColor(LIGHT)
    c.rect(10 * mm, band_y, 100 * mm, 12 * mm, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(14 * mm, band_y + 4 * mm, ticket.category.name.upper())
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(ORANGE)
    c.drawRightString(106 * mm, band_y + 4 * mm,
                      f"{int(ticket.category.price):,} FCFA".replace(",", " "))

    # --- Porteur ---
    porteur_y = band_y - 12 * mm
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8)
    c.drawString(10 * mm, porteur_y, "PORTEUR")
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(10 * mm, porteur_y - 5 * mm, ticket.holder_name or "—")
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY)
    c.drawString(10 * mm, porteur_y - 9 * mm, ticket.holder_email or "")
    c.drawString(10 * mm, porteur_y - 13 * mm, ticket.holder_phone or "")

    # --- QR ---
    qr_size = 45 * mm
    qr_x = page_w - qr_size - 10 * mm
    qr_y = page_h - qr_size - 35 * mm

    if ticket.qr_code_image and os.path.exists(ticket.qr_code_image.path):
        c.drawImage(
            ImageReader(ticket.qr_code_image.path),
            qr_x, qr_y, width=qr_size, height=qr_size,
            preserveAspectRatio=True, mask="auto",
        )
    else:
        c.setStrokeColor(GREY)
        c.rect(qr_x, qr_y, qr_size, qr_size, stroke=1, fill=0)
        c.setFont("Helvetica", 8)
        c.drawString(qr_x + 5 * mm, qr_y + qr_size / 2, "QR indisponible")

    c.setFont("Helvetica", 7)
    c.setFillColor(GREY)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 5 * mm, "Scannez à l'entrée")

    # --- Pied de page ---
    c.setFillColor(GREEN)
    c.rect(0, 0, page_w, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7)
    c.drawString(10 * mm, 3 * mm, "Billet nominatif — non transférable. Présentez ce QR à l'entrée.")
    c.drawRightString(page_w - 10 * mm, 3 * mm, "stadium-pass.ci")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()