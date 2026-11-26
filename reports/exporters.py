import csv
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

def export_orders_csv(queryset):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="ordens-box-box.csv"'
    response.write("\ufeff")
    writer = csv.writer(response); writer.writerow(["Ordem", "Data", "Cliente", "Placa", "Veículo", "Status", "Mecânico", "Valor final"])
    for o in queryset:
        writer.writerow([o.number, o.opened_at.strftime("%d/%m/%Y"), o.vehicle.owner.name, o.vehicle.plate, f"{o.vehicle.brand} {o.vehicle.model}", o.get_status_display(), o.mechanic or "", o.final_value or ""])
    return response

def export_orders_pdf(queryset):
    buffer = BytesIO(); pdf = canvas.Canvas(buffer, pagesize=landscape(A4)); width, height = landscape(A4)
    pdf.setTitle("Relatório Box Box"); pdf.setFont("Helvetica-Bold", 18); pdf.drawString(36, height-40, "BOX BOX · RELATÓRIO DE ORDENS")
    y = height - 72; pdf.setFont("Helvetica", 8)
    rows = list(queryset)
    if not rows: pdf.drawString(36, y, "Nenhuma ordem encontrada para os filtros selecionados.")
    for o in rows:
        pdf.drawString(36, y, f"{o.number}  |  {o.vehicle.plate}  |  {o.vehicle.owner.name[:30]}  |  {o.get_status_display()}")
        y -= 16
        if y < 36: pdf.showPage(); y = height - 40; pdf.setFont("Helvetica", 8)
    pdf.save(); response = HttpResponse(buffer.getvalue(), content_type="application/pdf"); response["Content-Disposition"] = 'attachment; filename="ordens-box-box.pdf"'; return response
