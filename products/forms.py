
from django import forms


class ProductSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        max_length=100,
        label="Search products",
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search products...",
                "class": "search-input",
                "aria-label": "Search products",
                "autocomplete": "off",
            }
        ),
    )
