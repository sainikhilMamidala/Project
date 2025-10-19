
from django import forms
from .models import Donation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['food_item', 'quantity', 'expiry_date']
