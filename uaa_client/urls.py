from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^callback$', views.oauth2_callback, name='callback'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
)
