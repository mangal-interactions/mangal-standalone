from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
#from mangalweb.apires imort *
from api.resources import *

v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(TaxaResource())
v1_api.register(InteractionResource())
v1_api.register(NetworkResource())
v1_api.register(DatasetResource())
v1_api.register(RefResource())
v1_api.register(TraitResource())
v1_api.register(EnvironmentResource())
v1_api.register(ItemResource())

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'base.views.index', name='index'),
    url(r'^api/', include(v1_api.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
