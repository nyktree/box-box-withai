from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from trash.services import archive_object

from .forms import UserForm
from .permissions import ROLE_ADMIN, role_required


@role_required(ROLE_ADMIN)
def user_list(request):
    return render(request, "accounts/user_list.html", {"users": User.objects.filter(is_active=True).order_by("username")})


@role_required(ROLE_ADMIN)
def user_create(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Usuário criado com sucesso.")
        return redirect("user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "Novo usuário"})


@role_required(ROLE_ADMIN)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    initial = {"role": user.groups.values_list("name", flat=True).first()}
    form = UserForm(request.POST or None, instance=user, initial=initial)
    if form.is_valid():
        form.save()
        messages.success(request, "Usuário atualizado.")
        return redirect("user_list")
    return render(request, "accounts/user_form.html", {"form": form, "title": "Editar usuário"})


@role_required(ROLE_ADMIN)
def user_deactivate(request, pk):
    if request.method != "POST":
        raise PermissionDenied

    if request.user.pk == pk:
        messages.error(request, "Você não pode arquivar o próprio usuário conectado.")
    else:
        archive_object(get_object_or_404(User, pk=pk), request.user)
        messages.success(request, "Usuário movido para a lixeira.")
    return redirect("user_list")
