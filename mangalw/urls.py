from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
#from mangalweb.apires imort *
from test_api.resources import *

vtest_api = Api(api_name='v1')
vtest_api.register(UserResource())
vtest_api.register(TaxaResource())
vtest_api.register(InteractionResource())
vtest_api.register(NetworkResource())
vtest_api.register(DatasetResource())
vtest_api.register(RefResource())
vtest_api.register(TraitResource())
vtest_api.register(EnvironmentResource())
vtest_api.register(ItemResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'base.views.index', name='index'),
    url(r'^globi.json$', 'base.views.globi', name='globi'),
    url(r'^api/', include(vtest_api.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
