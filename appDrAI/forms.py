from django import forms
from .models import *

class AiaForm(forms.ModelForm):
    class Meta:
        model = AiaFile
        fields = ('aia_file',)

class DataForm(forms.ModelForm):
    class Meta:
        model = DataModel
        fields = ('name','screens','naming','cond_if','cond_else','cond_elseif',
                'events','loop_while','loop_range','loop_list','proc','lists')
