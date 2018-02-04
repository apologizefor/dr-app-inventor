import os
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .forms import *
from django.shortcuts import redirect
from .appInstructor import *
from django.conf import settings

def file_form_page(request):
    if request.method == "GET":
        form = AiaForm()
        return render(request, 'appDrAI/upload.html',{'form': form})
    if request.method == "POST":
        form = AiaForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['aia_file']
            ext = str(f).split('.')[1]
            if ext == "aia":
                scr, naming, cond, ev, loop, proc, lists = (extractData(request.user.username,f))
                data = {"scr": scr, "naming":naming*100, 'if':cond['if'],
                        'else':cond['else'], 'elseif':cond['elseif'],
                        'events':ev, 'while':loop['while'], 'for_range':loop['range'],
                        'for_list':loop['list'],'proc':proc,'lists':lists,}
                project = DataModel()
                project.saveData(data,f.name)
                return redirect('results',pk=project.id_number)
    return render(request, 'appDrAI/upload.html',{'form': form})

def showResults(request,pk):
    project = get_object_or_404(DataModel, pk=pk)
    data = project.loadData()
    return render(request, 'appDrAI/results.html',data)

def showBN(request,pk):
    project = get_object_or_404(DataModel, pk=pk)
    return render(request, 'appDrAI/badnaming.html', {'naming': project.naming})
