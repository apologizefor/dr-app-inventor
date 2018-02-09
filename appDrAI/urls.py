from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.file_form_page,name='main'),
    #url(r'uploads/$', views.file_form_page,name='upload'),
    url(r'projects/$', views.projects_views,name='projects'),
    url(r'profile/projects/(?P<pk>[0-9]+)/$', views.showResults, name='results'),
    url(r'(?P<pk>[0-9]+)/bad-naming$', views.showBN, name='bad-naming'),
    url(r'profile/$',views.profile_view, name="profile"),
    url(r'registration/$',views.create_user,name="registration"),
    url(r'registration/login/$', views.login_page, name="login"),
    url(r'registration/logout/$', views.logout_page, name="logout"),
]
