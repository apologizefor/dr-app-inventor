from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm


class AiaForm(forms.Form):
    aia_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'filestyle','data-buttontext':'Elige Proyecto'}))
"""
class AiaForm(forms.ModelForm):
    class Meta:
        model = AiaFile
        fields = ('aia_file',)
"""
class DataForm(forms.ModelForm):
    class Meta:
        model = DataModel
        fields = ('name','screens','naming','cond','events','loop','proc','lists',
                'data_pers','author','sensors','media','social','connect','draw','operator','ui',)

class UserForm(UserCreationForm):
    first_name = forms.CharField()
    #first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder' : 'First Name ...'}))
    last_name = forms.CharField()
    email=forms.EmailField()
    app_inventor_name = forms.CharField()
