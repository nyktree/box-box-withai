from django import forms
from .models import Customer, Vehicle


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "document", "phone", "email", "address", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ("owner", "plate", "brand", "model", "year", "color", "mileage", "chassis", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
