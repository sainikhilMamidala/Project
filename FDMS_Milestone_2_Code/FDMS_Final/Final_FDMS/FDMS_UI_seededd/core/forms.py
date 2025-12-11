from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Donation
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta

User = get_user_model()

class DonorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ReceiverSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class DonationForm(forms.ModelForm):

    # Quantity field with bootstrap styling
    initial_quantity = forms.IntegerField(
        label="Quantity",
        min_value=1,
        required=True,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    # Expiry date with calendar picker + styling
    expiry_date = forms.DateField(
    required=False,
    widget=forms.DateInput(
        attrs={
            "type": "date",
            "class": "form-control",
            "min": (timezone.now().date() + timedelta(days=1)).isoformat(),
        }
    )
)

    # <-- Add donation_type as a ChoiceField here (no DB migration needed) -->
    DONATION_TYPE_CHOICES = [
        ("Other", "Other"),
        ("Frozen", "Frozen"),
        ("Cooked", "Cooked"),
        ("Fresh", "Fresh"),
    ]
    donation_type = forms.ChoiceField(
        choices=DONATION_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Donation
        fields = [
            "title",
            "location",
            "address",
            "initial_quantity",
            "expiry_date",
            "donation_type",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.Select(attrs={"class": "form-select"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            # donation_type is defined above; widget shown from field
        }

    def __init__(self, *args, **kwargs):
        # allow passing user in for future use (admin, staff behavior)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # donors should not set donor/claimed_by fields in this form
        self.fields.pop("donor", None)
        self.fields.pop("claimed_by", None)
