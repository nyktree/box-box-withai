from django.urls import path
from . import views
urlpatterns = [
 path("", views.order_list, name="order_list"), path("nova/", views.order_create, name="order_create"),
 path("<int:pk>/", views.order_detail, name="order_detail"), path("<int:pk>/editar/", views.order_update, name="order_update"),
 path("<int:pk>/arquivar/", views.order_archive, name="order_archive"),
 path("<int:pk>/status/", views.order_transition, name="order_transition"), path("<int:pk>/reabrir/", views.order_reopen, name="order_reopen"), path("<int:pk>/avarias/nova/", views.damage_create, name="damage_create"),
 path("<int:pk>/pecas/nova/", views.service_part_create, name="service_part_create"),
 path("pecas/", views.part_list, name="part_list"), path("pecas/nova/", views.part_create, name="part_create"),
 path("pecas/<int:pk>/editar/", views.part_update, name="part_update"), path("pecas/<int:pk>/desativar/", views.part_deactivate, name="part_deactivate"),
]
