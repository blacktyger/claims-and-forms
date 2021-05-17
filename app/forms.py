from django import forms
from .models import *


class EIOUForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['files', 'details', 'telegram', 'vitex_address']


