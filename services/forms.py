from django import forms
from .models import Damage, Part, ServiceOrder, ServicePart

class ServiceOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "vehicle" in self.fields:
            self.fields["vehicle"].queryset = self.fields["vehicle"].queryset.filter(is_active=True, owner__is_active=True)
        if "mechanic" in self.fields:
            self.fields["mechanic"].queryset = self.fields["mechanic"].queryset.filter(is_active=True, groups__name="Mecânico")
    class Meta:
        model = ServiceOrder
        fields = ("vehicle", "mechanic", "expected_delivery", "entry_mileage", "complaint", "notes", "estimated_value", "final_value")
        widgets = {"expected_delivery": forms.DateInput(attrs={"type": "date"}), "complaint": forms.Textarea(attrs={"rows": 3}), "notes": forms.Textarea(attrs={"rows": 3})}

class AttendantOrderForm(ServiceOrderForm):
    class Meta(ServiceOrderForm.Meta):
        fields = ("vehicle", "mechanic", "expected_delivery", "entry_mileage", "complaint", "estimated_value")

class MechanicOrderForm(ServiceOrderForm):
    class Meta(ServiceOrderForm.Meta):
        fields = ("notes",)

class DamageForm(forms.ModelForm):
    class Meta:
        model = Damage
        fields = ("category", "title", "symptom", "diagnosis", "confirmed_cause", "custom_cause", "severity", "resolved")

class ServicePartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["part"].queryset = self.fields["part"].queryset.filter(is_active=True)
    class Meta:
        model = ServicePart
        fields = ("damage", "part", "quantity", "unit_price")

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ("name", "code", "description", "stock_quantity", "unit_price", "is_active")
