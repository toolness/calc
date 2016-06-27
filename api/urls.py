from django.conf.urls import patterns, url
from api import views

urlpatterns = patterns(
    '',
    url(r'^rates/$', views.GetRates.as_view()),
    url(r'^rates/csv/$', views.GetRatesCSV.as_view()),
    url(r'^search/$', views.GetAutocomplete.as_view()),
)
