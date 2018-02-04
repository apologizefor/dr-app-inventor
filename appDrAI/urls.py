from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.file_form_page),
    url(r'projects/results/(?P<pk>[0-9]+)/$', views.showResults, name='results'),
    url(r'(?P<pk>[0-9]+)/bad-naming$', views.showBN, name='bad-naming'),
]
