from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = patterns('',
    url(r'^rates/$', views.GetRates.as_view()),
    url(r'^rates/csv/$', views.GetRatesCSV.as_view()),
    url(r'^search/', views.GetAutocomplete.as_view()),
)

#urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html', 'csv'])
