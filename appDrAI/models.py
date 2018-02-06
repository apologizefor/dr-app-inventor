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
    naming = models.FloatField()
    cond_if = models.IntegerField()
    cond_else = models.IntegerField()
    cond_elseif = models.IntegerField()
    events = models.IntegerField()
    loop_while = models.IntegerField()
    loop_range = models.IntegerField()
    loop_list = models.IntegerField()
    proc = models.IntegerField()
    lists = models.IntegerField()

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
        self.cond_if= data['if']
        self.cond_else = data['else']
        self.cond_elseif = data['elseif']
        self.events = data['events']
        self.loop_while = data['while']
        self.loop_range = data['for_range']
        self.loop_list = data['for_list']
        self.proc = data['proc']
        self.lists = data['lists']
        self.save()

    def loadData(self):
        data = {"name":self.name,"scr":self.screens, "naming":self.naming, 'if':self.cond_if,
                'else':self.cond_else, 'elseif':self.cond_elseif, 'events':self.events,
                'while':self.loop_while, 'for_range':self.loop_range, 'for_list':self.loop_list,
                'proc': self.proc,'lists':self.lists}
        return data
