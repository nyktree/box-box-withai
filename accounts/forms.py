from django import forms
from django.contrib.auth.models import Group, User
from .permissions import ROLES


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(choices=[(r, r) for r in ROLES])

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            user.groups.clear()
            user.groups.add(Group.objects.get(name=self.cleaned_data["role"]))
        return user
