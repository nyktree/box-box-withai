from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, role_required, user_has_role
from .domain import ensure_order_editable, reopen_order, transition_order
from .forms import AttendantOrderForm, DamageForm, MechanicOrderForm, PartForm, ServiceOrderForm, ServicePartForm
from .models import Part, ServiceOrder
from trash.services import archive_object

ALLOWED = (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)

@role_required(*ALLOWED)
def order_list(request):
    orders = ServiceOrder.objects.filter(is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True).select_related("vehicle", "vehicle__owner", "mechanic")
    q = request.GET.get("q", "").strip(); status = request.GET.get("status", "")
    if q: orders = orders.filter(Q(number__icontains=q) | Q(vehicle__plate__icontains=q) | Q(vehicle__owner__name__icontains=q))
    if status: orders = orders.filter(status=status)
    customer_groups = []
    groups_by_customer = {}
    for order in orders:
        customer = order.vehicle.owner
        group = groups_by_customer.get(customer.pk)
        if group is None:
            group = {"customer": customer, "orders": [], "vehicle_ids": set()}
            groups_by_customer[customer.pk] = group
            customer_groups.append(group)
        group["orders"].append(order)
        group["vehicle_ids"].add(order.vehicle_id)
    for group in customer_groups:
        group["order_count"] = len(group["orders"])
        group["vehicle_count"] = len(group.pop("vehicle_ids"))
    return render(request, "services/order_list.html", {"orders": orders, "customer_groups": customer_groups, "statuses": ServiceOrder.Status.choices, "query": q, "selected_status": status})

@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def order_create(request):
    form = ServiceOrderForm(request.POST or None)
    if form.is_valid():
        order = form.save(commit=False); order.attendant = request.user; order.save(); messages.success(request, "Ordem aberta."); return redirect("order_detail", pk=order.pk)
    return render(request, "services/order_form.html", {"form": form, "title": "Nova ordem", "responsible_user": request.user})

@role_required(*ALLOWED)
def order_detail(request, pk):
    order = get_object_or_404(ServiceOrder.objects.filter(is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True).select_related("vehicle", "vehicle__owner", "mechanic", "attendant"), pk=pk)
    is_admin = request.user.is_superuser or user_has_role(request.user, ROLE_ADMIN)
    is_assigned_mechanic = user_has_role(request.user, ROLE_MECHANIC) and order.mechanic_id == request.user.id
    is_final = order.status in {ServiceOrder.Status.DELIVERED, ServiceOrder.Status.CANCELLED}
    return render(request, "services/order_detail.html", {
        "order": order,
        "statuses": ServiceOrder.Status.choices,
        "can_edit_order": _can_edit(request.user, order) and not is_final,
        "can_manage_order_technical": (is_admin or is_assigned_mechanic) and not is_final,
        "can_transition_order": (is_admin or user_has_role(request.user, ROLE_ATTENDANT) or is_assigned_mechanic) and not is_final,
        "can_reopen_order": is_admin,
    })

def _can_edit(user, order):
    return user.is_superuser or user_has_role(user, ROLE_ADMIN) or user_has_role(user, ROLE_ATTENDANT) or (user_has_role(user, ROLE_MECHANIC) and order.mechanic_id == user.id)

@role_required(*ALLOWED)
def order_update(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True)
    ensure_order_editable(order)
    if not _can_edit(request.user, order): raise PermissionDenied
    form_class = ServiceOrderForm if user_has_role(request.user, ROLE_ADMIN) else (MechanicOrderForm if user_has_role(request.user, ROLE_MECHANIC) else AttendantOrderForm)
    form = form_class(request.POST or None, instance=order)
    if form.is_valid(): form.save(); return redirect("order_detail", pk=pk)
    return render(request, "services/order_form.html", {"form": form, "title": f"Editar {order.number}"})

@role_required(*ALLOWED)
def order_transition(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True)
    if request.method == "POST": transition_order(order, request.POST.get("status"), request.user, request.POST.get("note", "")); messages.success(request, "Status atualizado.")
    return redirect("order_detail", pk=pk)

@role_required(ROLE_ADMIN, ROLE_MECHANIC)
def damage_create(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True)
    ensure_order_editable(order)
    if user_has_role(request.user, ROLE_MECHANIC) and not (request.user.is_superuser or user_has_role(request.user, ROLE_ADMIN)) and order.mechanic_id != request.user.id: raise PermissionDenied
    form = DamageForm(request.POST or None)
    if form.is_valid(): damage = form.save(commit=False); damage.order = order; damage.save(); return redirect("order_detail", pk=pk)
    return render(request, "services/damage_form.html", {"form": form, "order": order})

@role_required(*ALLOWED)
def part_list(request):
    return render(request, "services/part_list.html", {"parts": Part.objects.filter(is_active=True).order_by("name")})

@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def part_create(request):
    form = PartForm(request.POST or None)
    if form.is_valid(): form.save(); return redirect("part_list")
    return render(request, "services/part_form.html", {"form": form, "title": "Nova peça"})

@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def part_update(request, pk):
    part = get_object_or_404(Part, pk=pk); form = PartForm(request.POST or None, instance=part)
    if form.is_valid(): form.save(); return redirect("part_list")
    return render(request, "services/part_form.html", {"form": form, "title": "Editar peça"})

@role_required(ROLE_ADMIN)
def part_deactivate(request, pk):
    if request.method != "POST": raise PermissionDenied
    archive_object(get_object_or_404(Part, pk=pk), request.user)
    return redirect("part_list")

@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def order_archive(request, pk):
    if request.method != "POST": raise PermissionDenied
    archive_object(get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True), request.user)
    messages.success(request, "Ordem movida para a lixeira.")
    return redirect("order_list")

@role_required(ROLE_ADMIN, ROLE_MECHANIC)
def service_part_create(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True)
    ensure_order_editable(order)
    if user_has_role(request.user, ROLE_MECHANIC) and not (request.user.is_superuser or user_has_role(request.user, ROLE_ADMIN)) and order.mechanic_id != request.user.id: raise PermissionDenied
    form = ServicePartForm(request.POST or None)
    if form.is_valid():
        used = form.save(commit=False); used.order = order
        if not used.unit_price: used.unit_price = used.part.unit_price
        used.save(); return redirect("order_detail", pk=pk)
    return render(request, "services/service_part_form.html", {"form": form, "order": order})

@role_required(ROLE_ADMIN)
def order_reopen(request, pk):
    order = get_object_or_404(ServiceOrder, pk=pk, is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True)
    if request.method != "POST": raise PermissionDenied
    reopen_order(order, request.user, request.POST.get("justification", ""))
    messages.success(request, "Ordem reaberta e auditoria registrada.")
    return redirect("order_detail", pk=pk)
