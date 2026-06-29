from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import password_change_required
from accounts.forms import (
    ForcePasswordChangeForm,
    InternalPasswordResetForm,
    InternalUserCreateForm,
    InternalUserEditForm,
)
from accounts.services.user_service import (
    create_internal_user,
    list_internal_users,
    mark_password_changed,
    reset_internal_user_password,
    toggle_user_active,
    update_internal_user,
)


User = get_user_model()


@login_required
@password_change_required
@permission_required("accounts.manage_internal_users", raise_exception=True)
def user_list(request):
    users = list_internal_users()
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
@password_change_required
@permission_required("accounts.manage_internal_users", raise_exception=True)
def user_create(request):
    if request.method == "POST":
        form = InternalUserCreateForm(request.POST)
        if form.is_valid():
            user = create_internal_user(form.cleaned_data)
            messages.success(request, f"Usuário {user.username} criado.")
            return redirect("accounts:user_list")
    else:
        form = InternalUserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Criar usuário",
            "submit_label": "Criar usuário",
        },
    )


@login_required
@password_change_required
@permission_required("accounts.manage_internal_users", raise_exception=True)
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = InternalUserEditForm(request.POST, instance=user)
        if form.is_valid():
            update_internal_user(user, form.cleaned_data, request.user)
            messages.success(request, f"Usuário {user.username} atualizado.")
            return redirect("accounts:user_list")
    else:
        form = InternalUserEditForm(instance=user)

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": f"Editar usuário: {user.username}",
            "submit_label": "Salvar alterações",
            "target_user": user,
        },
    )


@login_required
@password_change_required
@permission_required("accounts.manage_internal_users", raise_exception=True)
def user_toggle_active(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        toggle_user_active(user, request.user)
        status = "ativado" if user.is_active else "desativado"
        messages.success(request, f"Usuário {user.username} {status}.")
        return redirect("accounts:user_list")

    return render(
        request,
        "accounts/user_confirm_deactivate.html",
        {"target_user": user},
    )


@login_required
@password_change_required
@permission_required(
    ("accounts.manage_internal_users", "accounts.reset_internal_user_password"),
    raise_exception=True,
)
def user_reset_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if request.method == "POST":
        form = InternalPasswordResetForm(user, request.POST)
        if form.is_valid():
            reset_internal_user_password(user, form.cleaned_data["password1"], request.user)
            messages.success(
                request,
                f"Senha temporária definida para {user.username}. O usuário deverá trocar no próximo login.",
            )
            return redirect("accounts:user_list")
    else:
        form = InternalPasswordResetForm(user)

    return render(
        request,
        "accounts/password_reset_internal.html",
        {"form": form, "target_user": user},
    )


@login_required
def force_password_change(request):
    if request.method == "POST":
        form = ForcePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            mark_password_changed(user)
            update_session_auth_hash(request, user)
            messages.success(request, "Senha alterada.")
            return redirect("core:home")
    else:
        form = ForcePasswordChangeForm(request.user)

    return render(request, "accounts/force_password_change.html", {"form": form})
