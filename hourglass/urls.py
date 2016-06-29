from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .robots import robots_txt


# http://stackoverflow.com/a/13186337
admin.site.login = login_required(admin.site.login)

urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'hourglass.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^xls/$', 'hourglass_site.views.import_xls',
        name='import_xls'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'),
        name='about'),
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tests/$', TemplateView.as_view(template_name='tests.html')),
    url(r'^robots.txt$', robots_txt),
    url(r'^auth/', include('uaa_client.urls', namespace='uaa_client')),
)

if settings.DEBUG:
    import fake_uaa_provider.urls

    urlpatterns += patterns('',
                            url(r'^', include(fake_uaa_provider.urls,
                                              namespace='fake_uaa_provider')),
                            )
