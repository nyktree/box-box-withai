from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("usuarios/", include("accounts.urls")),
    path("clientes/", include("customers.urls")),
    path("ordens/", include("services.urls")),
    path("relatorios/", include("reports.urls")),
    path("lixeira/", include("trash.urls")),
    path("", include("assistente.urls")),
    path("", include("core.urls")),
]
