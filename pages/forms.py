from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.validators import RegexValidator

class CustomSetPasswordForm(SetPasswordForm):
    new_password2 = None

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        return password1