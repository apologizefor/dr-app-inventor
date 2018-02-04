from django.contrib import admin
from .models import DataModel
from .forms import DataForm

class AdminDataModel(admin.ModelAdmin):
    list_display = ["name", "id_number"]
    form = DataForm
    list_filter = ["name"]
    #list_editable = ["name"]
    search_fields = ["name"]


admin.site.register(DataModel, AdminDataModel)
