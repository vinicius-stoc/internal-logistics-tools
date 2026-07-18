from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.services.access_label_service import get_group_display_name
from accounts.services.rbac_service import GROUP_PERMISSIONS


User = get_user_model()


def allowed_groups_queryset():
    return Group.objects.filter(name__in=GROUP_PERMISSIONS.keys()).order_by("name")


class BootstrapFormMixin:
    def apply_bootstrap_classes(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault("class", "form-check-input")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class InternalUserCreateForm(BootstrapFormMixin, forms.Form):
    username = forms.CharField(label="Usuário", max_length=150)
    first_name = forms.CharField(label="Nome", max_length=150, required=False)
    last_name = forms.CharField(label="Sobrenome", max_length=150, required=False)
    email = forms.EmailField(label="E-mail", required=False)
    password1 = forms.CharField(label="Senha temporária", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar senha temporária", widget=forms.PasswordInput)
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    is_active = forms.BooleanField(label="Usuário ativo", required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].queryset = allowed_groups_queryset()
        self.fields["groups"].label_from_instance = (
            lambda group: get_group_display_name(group.name)
        )
        self.apply_bootstrap_classes()

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Já existe um usuário com este login.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não conferem.")

        if password1:
            try:
                validate_password(password1)
            except ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data


class InternalUserEditForm(BootstrapFormMixin, forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        label="Grupos",
        queryset=Group.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "is_active", "groups"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
            "is_active": "Usuário ativo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["groups"].queryset = allowed_groups_queryset()
        self.fields["groups"].label_from_instance = (
            lambda group: get_group_display_name(group.name)
        )
        self.fields["groups"].initial = self.instance.groups.filter(
            name__in=GROUP_PERMISSIONS.keys()
        )
        self.apply_bootstrap_classes()


class InternalPasswordResetForm(BootstrapFormMixin, forms.Form):
    password1 = forms.CharField(label="Senha temporária", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar senha temporária", widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.apply_bootstrap_classes()

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "As senhas não conferem.")

        if password1:
            try:
                validate_password(password1, self.user)
            except ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data


class ForcePasswordChangeForm(BootstrapFormMixin, SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].label = "Nova senha"
        self.fields["new_password2"].label = "Confirmar nova senha"
        self.apply_bootstrap_classes()
