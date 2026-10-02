"""
Stadium Pass — Services du journal d'audit.
"""
import logging

from .models import AuditLog


logger = logging.getLogger(__name__)


def log_action(action, description, user=None, obj=None,
               model_name='', object_id='', metadata=None, request=None):
    """
    Écrit une entrée dans le journal d'audit.

    Args:
        action: valeur de AuditLog.Action
        description: phrase lisible par un humain
        user: utilisateur à l'origine de l'action (peut être None)
        obj: objet concerné (déduit model_name/object_id)
        model_name: nom du modèle (si obj absent)
        object_id: ID de l'objet (si obj absent)
        metadata: dict de contexte structuré
        request: HttpRequest (pour IP et user-agent)
    """
    if obj is not None:
        model_name = obj.__class__.__name__
        object_id = str(obj.pk)

    ip_address = None
    user_agent = ''
    if request is not None:
        ip_address = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR')
        )
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:300]

    try:
        return AuditLog.objects.create(
            user=user if (user and user.is_authenticated) else None,
            action=action,
            description=description,
            model_name=model_name,
            object_id=object_id,
            metadata=metadata,
            ip_address=ip_address or None,
            user_agent=user_agent,
        )
    except Exception as e:
        logger.exception(f"Erreur écriture AuditLog : {e}")
        return None
