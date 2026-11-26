from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from services.models import ServiceOrder


@login_required
def dashboard(request):
    orders = ServiceOrder.objects.filter(is_archived=False, vehicle__is_active=True, vehicle__owner__is_active=True).select_related("vehicle", "vehicle__owner", "mechanic")
    query = request.GET.get("q", "").strip()
    if query: orders = orders.filter(Q(number__icontains=query) | Q(vehicle__plate__icontains=query) | Q(vehicle__owner__name__icontains=query))
    active = orders.exclude(status__in=[ServiceOrder.Status.DELIVERED, ServiceOrder.Status.CANCELLED])
    counts = {row["status"]: row["total"] for row in active.values("status").annotate(total=Count("id"))}
    return render(request, "core/dashboard.html", {"orders": active[:12], "counts": counts, "query": query, "statuses": ServiceOrder.Status})
