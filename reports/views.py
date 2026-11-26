from django.shortcuts import render

from accounts.permissions import ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC, role_required
from services.models import ServiceOrder

from .exporters import export_orders_csv, export_orders_pdf
from .filters import build_order_queryset

@role_required(ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)
def report_index(request):
    orders = build_order_queryset(request.GET, request.user)
    return render(request, "reports/index.html", {"orders": orders[:100], "statuses": ServiceOrder.Status.choices})


@role_required(ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)
def report_csv(request):
    orders = build_order_queryset(request.GET, request.user)
    return export_orders_csv(orders)


@role_required(ROLE_ADMIN, ROLE_ATTENDANT, ROLE_MECHANIC)
def report_pdf(request):
    orders = build_order_queryset(request.GET, request.user)
    return export_orders_pdf(orders)
