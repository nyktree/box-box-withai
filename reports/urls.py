from django.urls import path
from . import views
urlpatterns = [path("", views.report_index, name="report_index"), path("csv/", views.report_csv, name="report_csv"), path("pdf/", views.report_pdf, name="report_pdf")]
