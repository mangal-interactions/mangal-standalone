from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
from api import *

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

urlpatterns = patterns('',)
