import os
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import *
from .forms import *
from django.shortcuts import redirect
from .appInstructor import *
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def main_view(request):
    #return render(request, 'drScratch/Dr. Scratch.html',{})
    return render(request, 'appDrAI/main.html',{})

def profile_view(request):
    if request.method == "GET":
        user = UserModel.objects.get(user_id=request.user.id)
        user_data = user.loadUserModel()
        proj =  DataModel.objects.filter(author_id=user.user_id)
        proj_data = []
        for element in proj:
            proj_data.append(element.loadNameID())
        return render(request, 'appDrAI/profile.html', user_data)

def projects_views(request):
    if request.method == "GET":
        user = UserModel.objects.get(user_id=request.user.id)
        proj =  DataModel.objects.filter(author_id=user.user_id)
        proj_data = []
        for element in proj:
            proj_data.append(element)
        context = {}
        if len(proj_data) > 0:
            context['proj_data']= proj_data
        return render(request, 'appDrAI/projects.html', context)

def file_form_page(request):
    if request.method == "GET":
        form = AiaForm()
        #return render(request, 'drScratch/Dr. Scratch.html',{})
        return render(request, 'appDrAI/upload.html',{'form': form})
    if request.method == "POST":
        form = AiaForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data['aia_file']
            ext = str(f).split('.')[1]
            if ext == "aia":
                scr, naming, cond, ev, loop, proc, lists, dp = (extractData(request.user.username,f))
                data = {"scr": scr, "naming":naming, 'conditional':cond,
                        'events':ev, 'loop':loop,'proc':proc,'lists':lists,
                        'dp':dp}
                project = DataModel()
                project.saveData(data,f.name,request.user.id)
                return redirect('results',pk=project.id_number)
    #return render(request, 'drScratch/Dr. Scratch.html',{})
    return render(request, 'appDrAI/upload.html',{'form': form})


def create_user(request):
    if request.method == "GET":
        form = UserForm()
        return render(request, 'appDrAI/registration.html',{'form': form})
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = UserModel()
            user.addUser(request.POST)
            #return redirect('main')
            return redirect('login')
    return render(request, 'appDrAI/registration.html',{'form': form})


def login_page(request):
    if request.method == "GET":
        form = AuthenticationForm()
        return render(request, 'appDrAI/registration.html',{'form': form})
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('upload')
        else:
            form = AuthenticationForm()
            return render(request, 'appDrAI/registration.html',{'form': form, 'error': True})

def logout_page(request):
    logout(request)
    return redirect('main')

def showResults(request,pk):
    project = get_object_or_404(DataModel, pk=pk)
    data = project.loadProject()
    total = 0;
    for key in data:
        total += data[key]
    context = {'data':data,'result':total,'max':len(data)*3}
    return render(request, 'drScratch/Dr.Scratch_show_dash.html',context)

def showBN(request,pk):
    project = get_object_or_404(DataModel, pk=pk)
    return render(request, 'appDrAI/badnaming.html', {'naming': project.naming})
