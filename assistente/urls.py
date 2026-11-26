from django.urls import path

from . import views

urlpatterns = [
    path("acompanhar/<str:token>/", views.acompanhar, name="cliente_acompanhar"),
    path("acompanhar/<str:token>/perguntar/", views.perguntar, name="cliente_perguntar"),
    path("assistente/ordens/<int:pk>/link/", views.gerar_link, name="assistente_gerar_link"),
    path("assistente/ordens/<int:pk>/link/revogar/", views.revogar_link, name="assistente_revogar_link"),
    path("assistente/api/classificar/", views.api_classificar, name="assistente_api_classificar"),
    path("assistente/api/metricas/", views.api_metricas, name="assistente_api_metricas"),
]
