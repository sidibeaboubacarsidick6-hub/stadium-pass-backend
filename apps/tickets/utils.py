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
