from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class AiaForm(forms.Form):
    attributes = {'class': 'filestyle', 'data-buttontext': 'Elige Proyecto'}
    aia_file = forms.FileField(widget=forms.FileInput(attrs=attributes))


class DataForm(forms.ModelForm):
    class Meta:
        model = DataModel
        fields = (
            'name', 'screens', 'naming', 'cond', 'events',
            'loop', 'proc', 'lists', 'data_pers', 'author',
            'sensors', 'media', 'social', 'connect', 'draw',
            'operator', 'ui'
            )


class UserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    app_inventor_name = forms.CharField()
