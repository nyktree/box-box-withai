from django.urls import path
from . import views
urlpatterns = [path("", views.trash_list, name="trash_list"), path("<int:pk>/restaurar/", views.trash_restore, name="trash_restore"), path("<int:pk>/excluir/", views.trash_delete, name="trash_delete"), path("esvaziar/", views.trash_empty, name="trash_empty")]
