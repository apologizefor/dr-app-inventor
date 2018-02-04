from django.db import models
from django.utils import timezone

class AiaFile(models.Model):
    aia_file = models.FileField()
    def __str__(self): #python3
        return self.name

class DataModel(models.Model):
    id_number = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
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

    def saveData(self,data,name):
        self.id_number=len(DataModel.objects.all())
        self.name= name
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
