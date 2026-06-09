from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    """Informations de livraison pour valider la commande."""

    class Meta:
        model = Order
        fields = ("full_name", "address", "city", "postal_code", "phone")
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }
