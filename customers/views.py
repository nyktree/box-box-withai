from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, role_required
from trash.services import archive_object

from .forms import CustomerForm, VehicleForm
from .models import Customer, Vehicle

ALLOWED = (ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)


@role_required(*ALLOWED)
def customer_list(request):
    query = request.GET.get("q", "").strip()
    customers = Customer.objects.filter(is_active=True)
    if query:
        customers = customers.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(document__icontains=query))
    return render(request, "customers/customer_list.html", {"customers": customers, "query": query})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def customer_create(request):
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        customer = form.save()
        messages.success(request, "Cliente cadastrado.")
        return redirect("customer_detail", pk=customer.pk)
    return render(request, "customers/customer_form.html", {"form": form, "title": "Novo cliente"})


@role_required(*ALLOWED)
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, is_active=True)
    vehicles = customer.vehicles.filter(is_active=True)
    return render(request, "customers/customer_detail.html", {"customer": customer, "vehicles": vehicles})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk, is_active=True)
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, "Cliente atualizado.")
        return redirect("customer_detail", pk=pk)
    return render(request, "customers/customer_form.html", {"form": form, "title": "Editar cliente"})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def customer_deactivate(request, pk):
    if request.method != "POST":
        raise PermissionDenied
    archive_object(get_object_or_404(Customer, pk=pk), request.user)
    return redirect("customer_list")


@role_required(*ALLOWED)
def vehicle_list(request):
    query = request.GET.get("q", "").strip()
    vehicles = Vehicle.objects.filter(is_active=True, owner__is_active=True).select_related("owner")
    if query:
        vehicles = vehicles.filter(
            Q(plate__icontains=query)
            | Q(model__icontains=query)
            | Q(owner__name__icontains=query)
        )
    return render(request, "customers/vehicle_list.html", {"vehicles": vehicles, "query": query})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def vehicle_create(request):
    owner_id = request.GET.get("owner")
    initial = {}
    if owner_id:
        owner = get_object_or_404(Customer, pk=owner_id, is_active=True)
        initial["owner"] = owner.pk
    form = VehicleForm(request.POST or None, initial=initial)
    if form.is_valid():
        vehicle = form.save()
        return redirect("vehicle_detail", pk=vehicle.pk)
    return render(request, "customers/vehicle_form.html", {"form": form, "title": "Novo veículo"})


@role_required(*ALLOWED)
def vehicle_detail(request, pk):
    vehicles = (
        Vehicle.objects.filter(is_active=True, owner__is_active=True)
        .select_related("owner")
        .prefetch_related("service_orders__damages", "service_orders__used_parts__part")
    )
    vehicle = get_object_or_404(vehicles, pk=pk)
    return render(request, "customers/vehicle_detail.html", {"vehicle": vehicle, "history": vehicle.service_orders.order_by("-opened_at")})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, is_active=True, owner__is_active=True)
    form = VehicleForm(request.POST or None, instance=vehicle)
    if form.is_valid():
        form.save()
        return redirect("vehicle_detail", pk=pk)
    return render(request, "customers/vehicle_form.html", {"form": form, "title": "Editar veículo"})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT)
def vehicle_deactivate(request, pk):
    if request.method != "POST":
        raise PermissionDenied
    archive_object(get_object_or_404(Vehicle, pk=pk), request.user)
    return redirect("vehicle_list")
