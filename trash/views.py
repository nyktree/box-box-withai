from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, role_required, user_has_role
from .models import TrashRecord
from .services import permanently_delete, restore_record

ALLOWED = (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)
PENDING = {"restored_at__isnull": True, "permanently_deleted_at__isnull": True}

def _allowed_types(user):
    if user.is_superuser or user_has_role(user, ROLE_ADMIN): return None
    if user_has_role(user, ROLE_ATTENDANT): return (("customers", "customer"), ("customers", "vehicle"), ("services", "serviceorder"))
    return ()

def _can_restore(user, record):
    allowed = _allowed_types(user)
    return allowed is None or (record.content_type.app_label, record.content_type.model) in allowed

@role_required(*ALLOWED)
def trash_list(request):
    records = TrashRecord.objects.filter(**PENDING).select_related("content_type", "archived_by")
    allowed = _allowed_types(request.user)
    query = None
    if allowed is not None:
        from django.db.models import Q
        for app_label, model in allowed:
            condition = Q(content_type__app_label=app_label, content_type__model=model)
            query = condition if query is None else query | condition
        records = records.filter(query) if query is not None else records.none()
    history = TrashRecord.objects.exclude(restored_at__isnull=True, permanently_deleted_at__isnull=True).select_related("content_type", "archived_by", "restored_by")
    if allowed is not None:
        history = history.filter(query) if query is not None else history.none()
    history = history[:100]
    return render(request, "trash/list.html", {"records": records, "history": history})

@role_required(*ALLOWED)
def trash_restore(request, pk):
    if request.method == "POST":
        record = get_object_or_404(TrashRecord.objects.select_related("content_type"), pk=pk, **PENDING)
        if not _can_restore(request.user, record): raise PermissionDenied
        try: restore_record(record, request.user); messages.success(request, "Registro restaurado.")
        except ValidationError as exc: messages.error(request, exc.message)
    return redirect("trash_list")

@role_required(ROLE_ADMIN)
def trash_delete(request, pk):
    if request.method == "POST":
        try: permanently_delete(get_object_or_404(TrashRecord, pk=pk, **PENDING), request.user); messages.success(request, "Registro excluído definitivamente.")
        except ValidationError as exc: messages.error(request, exc.message)
    return redirect("trash_list")

@role_required(ROLE_ADMIN)
def trash_empty(request):
    if request.method == "POST":
        deleted = blocked = 0
        for record in TrashRecord.objects.filter(restored_at__isnull=True, permanently_deleted_at__isnull=True):
            try: permanently_delete(record, request.user); deleted += 1
            except ValidationError: blocked += 1
        messages.success(request, f"Lixeira processada: {deleted} excluídos, {blocked} preservados por histórico.")
    return redirect("trash_list")
