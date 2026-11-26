from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, user_has_role

from .models import ServiceOrder, StatusHistory

FINAL_STATUSES = {ServiceOrder.Status.DELIVERED, ServiceOrder.Status.CANCELLED}


def ensure_order_editable(order):
    if order.status in FINAL_STATUSES:
        raise PermissionDenied("A ordem finalizada deve ser reaberta antes de qualquer alteração.")


TRANSITIONS = {
    ServiceOrder.Status.OPEN: {
        ServiceOrder.Status.WAITING_DIAGNOSIS,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.WAITING_DIAGNOSIS: {
        ServiceOrder.Status.WAITING_PARTS,
        ServiceOrder.Status.IN_MAINTENANCE,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.WAITING_PARTS: {
        ServiceOrder.Status.IN_MAINTENANCE,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.IN_MAINTENANCE: {
        ServiceOrder.Status.WAITING_PARTS,
        ServiceOrder.Status.READY,
        ServiceOrder.Status.CANCELLED,
    },
    ServiceOrder.Status.READY: {
        ServiceOrder.Status.DELIVERED,
        ServiceOrder.Status.IN_MAINTENANCE,
    },
    ServiceOrder.Status.DELIVERED: set(),
    ServiceOrder.Status.CANCELLED: set(),
}


def transition_order(order, new_status, actor, note=""):
    with transaction.atomic():
        order = ServiceOrder.objects.select_for_update().get(pk=order.pk)
        if new_status not in TRANSITIONS.get(order.status, set()):
            raise ValidationError("Transição de status inválida.")

        is_admin = actor.is_superuser or user_has_role(actor, ROLE_ADMIN)
        if not is_admin and user_has_role(actor, ROLE_MECHANIC) and order.mechanic_id != actor.id:
            raise PermissionDenied
        attendant_statuses = {
            ServiceOrder.Status.WAITING_DIAGNOSIS,
            ServiceOrder.Status.CANCELLED,
            ServiceOrder.Status.DELIVERED,
        }
        if not is_admin and user_has_role(actor, ROLE_ATTENDANT) and new_status not in attendant_statuses:
            raise PermissionDenied
        if new_status == ServiceOrder.Status.READY and not (order.notes.strip() or order.damages.exclude(diagnosis="").exists()):
            raise ValidationError("É necessário registrar diagnóstico ou observação técnica antes de concluir.")
        previous = order.status
        order.status = new_status
        if new_status == ServiceOrder.Status.DELIVERED:
            order.completed_at = timezone.now()
        order.save(update_fields=["status", "completed_at"])
        return StatusHistory.objects.create(order=order, previous_status=previous, new_status=new_status, actor=actor, note=note)


def reopen_order(order, actor, justification):
    with transaction.atomic():
        order = ServiceOrder.objects.select_for_update().get(pk=order.pk)
        if not user_has_role(actor, ROLE_ADMIN):
            raise PermissionDenied
        if order.status not in FINAL_STATUSES:
            raise ValidationError("A ordem não está finalizada.")
        if not justification.strip():
            raise ValidationError("Justificativa obrigatória.")

        previous = order.status
        order.status = ServiceOrder.Status.WAITING_DIAGNOSIS
        order.completed_at = None
        order.save(update_fields=["status", "completed_at"])
        return StatusHistory.objects.create(order=order, previous_status=previous, new_status=order.status, actor=actor, note=justification)
