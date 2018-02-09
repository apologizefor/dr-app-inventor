from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class AiaFile(models.Model):
    aia_file = models.FileField()
    def __str__(self): #python3
        return self.name

class UserModel(models.Model):
    id_number = models.AutoField(primary_key=True)
    user = models.OneToOneField(User)
    #projects = models.ForeignKey('UserModel',on_delete=models.CASCADE,null=True,blank=True)
    ainame = models.CharField(max_length=20)

    def addUser(self,data):
        new_user = User.objects.create_user(data['username'],data['email'],
                    data['password1'])
        new_user.save()
        self.user_id = new_user.pk
        self.ainame = data['app_inventor_name']
        self.save()

    def loadUserModel(self):
        data = {"name":self.user.username,"ainame":self.ainame,
                "email":self.user.email}

        return data

    def __str__(self):
        return self.ainame

class DataModel(models.Model):
    id_number = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    author = models.ForeignKey('UserModel',on_delete=models.CASCADE,null=True,blank=True)
    screens = models.IntegerField()
    naming = models.IntegerField()
    cond = models.IntegerField()
    events = models.IntegerField()
    loop = models.IntegerField()
    proc = models.IntegerField()
    data_pers = models.IntegerField()
    lists = models.IntegerField()
    sensors = models.IntegerField()
    media = models.IntegerField()
    social = models.IntegerField()
    connect = models.IntegerField()
    draw = models.IntegerField()
    operator = models.IntegerField()
    ui = models.IntegerField()

    def __str__(self): #python3
        return self.name

    def loadNameID(self):
        data = {'name':self.name, 'pk':self.pk}
        return data

    def saveData(self,data,name,user_id):
        self.name= name
        self.author_id = user_id
        self.screens= data['scr']
        self.naming= data['naming']
        self.cond= data['conditional']
        self.events = data['events']
        self.loop = data['loop']
        self.proc = data['proc']
        self.data_pers = data['dp']
        self.lists = data['lists']
        self.sensors = data['sensors']
        self.media = data['media']
        self.social = data['social']
        self.connect = data['connect']
        self.draw = data['draw']
        self.operator = data['operator']
        self.ui = data['ui']
        self.save()

    def loadProject(self):
        data = [{"scr":self.screens}, {"ui":self.ui}, {"naming":self.naming},{'events':self.events},
                {'proc': self.proc},{'loop':self.loop},{'conditional':self.cond},{'lists':self.lists},
                {'dp': self.data_pers}, {'sensors':self.sensors}, {'media':self.media},{'social':self.social},
                {'connect': self.connect}, {'draw': self.draw},{'operator':self.operator}]
        return data

    def loadData(self):
        data = {'name':self.name, 'scr':self.screens, "ui":self.ui, 'naming':self.naming, 'conditional':self.cond,
                'events':self.events, 'loop':self.loop, 'proc': self.proc,'lists':self.lists,
                'dp': self.data_pers, 'sensors':self.sensors,'media':self.media,'social':self.social,
                'connect': self.connect, 'draw': self.draw, 'operator':self.operator}
        return data
