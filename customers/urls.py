from django.urls import path
from . import views
urlpatterns = [
 path("", views.customer_list, name="customer_list"), path("novo/", views.customer_create, name="customer_create"),
 path("<int:pk>/", views.customer_detail, name="customer_detail"), path("<int:pk>/editar/", views.customer_update, name="customer_update"),
 path("<int:pk>/desativar/", views.customer_deactivate, name="customer_deactivate"),
 path("veiculos/", views.vehicle_list, name="vehicle_list"), path("veiculos/novo/", views.vehicle_create, name="vehicle_create"),
 path("veiculos/<int:pk>/", views.vehicle_detail, name="vehicle_detail"), path("veiculos/<int:pk>/editar/", views.vehicle_update, name="vehicle_update"),
 path("veiculos/<int:pk>/desativar/", views.vehicle_deactivate, name="vehicle_deactivate"),
]
