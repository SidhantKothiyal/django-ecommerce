
import re

from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        label="Full name",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "name",
                "placeholder": "Enter your full name",
            }
        ),
    )

    email = forms.EmailField(
        max_length=254,
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
                "placeholder": "Enter your email",
            }
        ),
    )

    phone = forms.RegexField(
        regex=r"^[0-9+\-\s()]{7,20}$",
        max_length=20,
        label="Phone number",
        error_messages={
            "invalid": "Enter a valid phone number.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "tel",
                "placeholder": "Enter your phone number",
                "inputmode": "tel",
            }
        ),
    )

    address_line1 = forms.CharField(
        max_length=255,
        label="Address line 1",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "address-line1",
                "placeholder": "House number, street, area",
            }
        ),
    )

    address_line2 = forms.CharField(
        max_length=255,
        required=False,
        label="Address line 2 (optional)",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "address-line2",
                "placeholder": "Apartment or landmark",
            }
        ),
    )

    city = forms.CharField(
        max_length=100,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "address-level2",
                "placeholder": "City",
            }
        ),
    )

    state = forms.CharField(
        max_length=100,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "address-level1",
                "placeholder": "State",
            }
        ),
    )

    postal_code = forms.RegexField(
        regex=r"^[0-9]{6}$",
        min_length=6,
        max_length=6,
        label="PIN code",
        error_messages={
            "invalid": "Enter a valid 6-digit Indian PIN code.",
        },
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "autocomplete": "postal-code",
                "placeholder": "6-digit PIN code",
                "maxlength": "6",
            }
        ),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip()

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        # Reject phone numbers containing no digits.
        if not re.search(r"\d", phone):
            raise forms.ValidationError(
                "Enter a phone number containing digits."
            )

        return phone
