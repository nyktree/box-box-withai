from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models.deletion import ProtectedError
from django.db import transaction
from django.utils import timezone
from accounts.permissions import ROLE_ADMIN, user_has_role
from .models import TrashRecord

def _ensure_pending(record):
    if record.restored_at or record.permanently_deleted_at:
        raise ValidationError("Este item não está mais ativo na lixeira.")

@transaction.atomic
def archive_object(obj, actor):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(obj)
    existing = TrashRecord.objects.filter(content_type=content_type, object_id=obj.pk, restored_at__isnull=True, permanently_deleted_at__isnull=True).first()
    if existing: return existing
    if hasattr(obj, "is_active"):
        obj.is_active = False; obj.save(update_fields=["is_active"])
    elif hasattr(obj, "is_archived"):
        obj.is_archived = True; obj.save(update_fields=["is_archived"])
    else:
        raise ValidationError("Este tipo de registro não pode ser arquivado.")
    return TrashRecord.objects.create_for_object(obj, actor)

@transaction.atomic
def restore_record(record, actor):
    _ensure_pending(record)
    obj = record.content_object
    if obj is None: raise ValidationError("O registro original não existe mais.")
    if hasattr(obj, "is_active"):
        obj.is_active = True; obj.save(update_fields=["is_active"])
    else:
        obj.is_archived = False; obj.save(update_fields=["is_archived"])
    record.restored_by = actor; record.restored_at = timezone.now(); record.save(update_fields=["restored_by", "restored_at"])
    return obj

@transaction.atomic
def permanently_delete(record, actor):
    if not user_has_role(actor, ROLE_ADMIN): raise PermissionDenied
    _ensure_pending(record)
    obj = record.content_object
    if obj is not None:
        try: obj.delete()
        except ProtectedError as exc: raise ValidationError("O registro possui histórico relacionado e não pode ser removido definitivamente.") from exc
    TrashRecord.objects.filter(pk=record.pk).update(permanently_deleted_at=timezone.now())
