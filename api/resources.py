from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, Authentication
from models import *
from django.contrib.auth.models import User
from django.db import IntegrityError
from tastypie.exceptions import BadRequest, Unauthorized
from django.db.models import Q

class MangalAuthorization(Authorization):

    def is_object_readable(self, ob, bundle):
        """ Is the object readable?

        An object is BY DEFAULT readable if the resource has no public field

        If there is a public field, the resource is only readable by
        (i)  staff
        (ii) the owner
        (iv) the public if public is True
        """
        try :
            ob.public
            ob.owner
        except AttributeError :
            return True
        except :
            # I don't know why it is needed, but the schemas are NOT
            # returned without that...
            return True
        else :
            if bundle.request.user.is_staff or ob.owner == bundle.request.user or ob.public:
                return True
            else :
                return False

    def read_list(self, object_list, bundle):
        return [ob for ob in object_list if self.is_object_readable(ob, bundle)]

    def read_detail(self, object_list, bundle):
        return self.is_object_readable(bundle.obj, bundle)

    def create_list(self, object_list, bundle):
        return True

    def create_detail(self, object_list, bundle):
        """Create an object

        The only condition is to be authenticated
        """
        return bundle.request.user.is_authenticated()

    def update_list(self, object_list, bundle):
        return [ob for ob in object_list if self.is_object_readable(ob, bundle)]

    def update_detail(self, object_list, bundle):
        return self.is_object_readable(bundle.obj, bundle)

    def delete_list(self, object_list, bundle):
        return [ob for ob in object_list if self.is_object_readable(ob, bundle)]

    def delete_detail(self, object_list, bundle):
        return True

class UserAuthorization(DjangoAuthorization):

    def read_list(self, object_list, bundle):
        return [ob for ob in object_list]

    def read_detail(self, object_list, bundle):
        return True

    def create_list(self, object_list, bundle):
        raise Unauthorized("No creating a bunch of users (for now)")

    def create_detail(self, object_list, bundle):
        raise Unauthorized("Users can be created on the web interface")

    def update_list(self, object_list, bundle):
        raise Unauthorized("No updating users")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("No updating users")

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Deleting users is not permitted")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Deleting users is not permitted")

class UserResource(ModelResource):
    class Meta:
        object_class = User
        #authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = UserAuthorization()
        queryset = User.objects.all()
        always_return_data = True
        resource_name = 'user'
        excludes = ['date_joined', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'password']
        filtering = {'username': ALL, 'email': ALL, 'last_name': ALL, 'first_name': ALL, }
        allowed_methods = ['get']
    def obj_create(self, bundle, request=None, **kwargs):
        username, password = bundle.data['username'], bundle.data['password']
        try :
            bundle.obj = User.objects.create_user(username, '', password)
        except IntegrityError:
            raise BadRequest('That username already exists')
        return bundle


class RefResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "URI of the profile of the owner. When objects are uploaded from the R package, this field is set automatically.")
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Ref.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'reference'
        #list_allowed_methods = ['get']
        #detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class TraitResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Trait.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'trait'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class EnvironmentResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Environment.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'environment'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class TaxaResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "URI of the taxa owner. When submitting from the R package, this field is populated automatically.")
    traits = fields.ManyToManyField(TraitResource, 'traits', full=True, blank = True, null = True, help_text = "A list of traits values indentifiers (or URIs) that were measured on this taxa. Good for taxa-level traits.")
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['traits'] = [str(tr.data['id']) for tr in bundle.data['traits']]
        return bundle
    def build_schema(self):
        base_schema = super(TaxaResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': [cho[0] for cho in f.choices],
                    })
        return base_schema
    class Meta:
        queryset = Taxa.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'taxa'
        filtering = {
                'name': ALL,
                'vernacular': ALL,
                'gbif': ALL,
                'eol': ALL,
                'itis': ALL,
                'ncbi': ALL,
                'bold': ALL,
                'owner': ALL,
                'filter': ALL,
                }
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']

class ItemResource(ModelResource):
    taxa = fields.ForeignKey(TaxaResource, 'taxa', full=True, help_text = "The identifier (or URI) of the taxa object to which the item belongs.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    traits = fields.ManyToManyField(TraitResource, 'traits', full=True, blank = True, null = True, help_text = "A list of traits values indentifiers (or URIs) that were measured on this item.")
    def dehydrate(self, bundle):
        bundle.data['taxa'] = str(bundle.obj.taxa_id)
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['traits'] = [str(tr.data['id']) for tr in bundle.data['traits']]
        return bundle
    def build_schema(self):
        base_schema = super(ItemResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': [cho[0] for cho in f.choices],
                    })
        return base_schema
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        queryset = Item.objects.all()
        filtering = {
                'taxa': ALL_WITH_RELATIONS,
                'description': ALL,
                'owner': ALL_WITH_RELATIONS,
                'stage': ALL,
                'level': ALL,
                }
        resource_name = 'item'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class InteractionResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner', full=True, help_text = "Who uploaded the data. URI of the data owner.", null=True, blank=True)
    environment = fields.ManyToManyField(EnvironmentResource, 'environment', full=True, help_text = "List of identifiers (or URIs) of the environments associated to the interaction.", null=True, blank=True)
    taxa_from = fields.ForeignKey(TaxaResource, 'taxa_from', full=True, help_text = "Identifier (or URI) of the taxa establishing the interaction.")
    taxa_to = fields.ForeignKey(TaxaResource, 'taxa_to', full=True, help_text = "Identifier (or URI) of the taxa receiving the interaction.")
    item_from = fields.ForeignKey(ItemResource, 'item_from', full=True, null = True, blank = True, help_text = "Identifier (or URI) of the item establishing the interaction.")
    item_to = fields.ForeignKey(ItemResource, 'item_to', full=True, null = True, blank = True, help_text = "Identifier (or URI) of the item receiving the interaction.")
    data = fields.ManyToManyField(RefResource, 'data', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references describing the data.")
    papers = fields.ManyToManyField(RefResource, 'papers', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references to the papers associated with the dataset.")
    def build_schema(self):
        base_schema = super(InteractionResource, self).build_schema()
        for f in self._meta.object_class._meta.fields:
            if f.name in base_schema['fields'] and f.choices:
                base_schema['fields'][f.name].update({
                    'choices': [cho[0] for cho in f.choices],
                    })
        return base_schema
    def dehydrate(self, bundle):
        bundle.data['data'] = [str(ref.data['id']) for ref in bundle.data['data']]
        bundle.data['papers'] = [str(ref.data['id']) for ref in bundle.data['papers']]
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['taxa_from'] = str(bundle.data['taxa_from'].obj.id)
        bundle.data['environment'] = [str(env.data['id']) for env in bundle.data['environment']]
        bundle.data['taxa_to'] = str(bundle.data['taxa_to'].obj.id)
        if bundle.data['item_from']:
            bundle.data['item_from'] = str(bundle.data['item_from'].obj.id)
        if bundle.data['item_to']:
            bundle.data['item_to'] = str(bundle.data['item_to'].obj.id)
        return bundle
    class Meta:
        queryset = Interaction.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'taxa_from': ALL_WITH_RELATIONS,
                'taxa_to': ALL_WITH_RELATIONS,
                'item_to': ALL_WITH_RELATIONS,
                'item_from': ALL_WITH_RELATIONS,
                'link_type': ALL_WITH_RELATIONS,
                'obs_type': ALL_WITH_RELATIONS,
                'nature': ALL_WITH_RELATIONS,
                'description': ALL,
                }
        resource_name = 'interaction'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class NetworkResource(ModelResource):
    interactions = fields.ManyToManyField(InteractionResource, 'interactions', full=True, help_text = "List of identifiers (or URIs) of the interactions in the network.")
    environment = fields.ManyToManyField(EnvironmentResource, 'environment', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of environmental measurements associated to the network.")
    data = fields.ManyToManyField(RefResource, 'data', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references describing the data.")
    papers = fields.ManyToManyField(RefResource, 'papers', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references to the papers associated with the dataset.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['interactions'] = [str(inte.data['id']) for inte in bundle.data['interactions']]
        bundle.data['environment'] = [str(env.data['id']) for env in bundle.data['environment']]
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        bundle.data['data'] = [str(ref.data['id']) for ref in bundle.data['data']]
        bundle.data['papers'] = [str(ref.data['id']) for ref in bundle.data['papers']]
        return bundle
    class Meta:
        queryset = Network.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'network'
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'interactions': ALL_WITH_RELATIONS,
                'metaweb': ALL_WITH_RELATIONS,
                'description': ALL,
                'name': ALL,
                'latitude': ALL_WITH_RELATIONS,
                'longitude': ALL_WITH_RELATIONS,
                }
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']


class DatasetResource(ModelResource):
    networks = fields.ManyToManyField(NetworkResource, 'networks', full=True, help_text = "List of identifiers (or URIs) of the networks in the dataset.")
    environment = fields.ManyToManyField(EnvironmentResource, 'environment', full=True, help_text = "List of identifiers (or URIs) of the environments associated to the dataset.", null=True, blank=True)
    data = fields.ManyToManyField(RefResource, 'data', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references describing the data.")
    papers = fields.ManyToManyField(RefResource, 'papers', full=True, null=True, blank=True, help_text = "List of identifiers (or URIs) of the references to the papers associated with the dataset.")
    owner = fields.ForeignKey(UserResource, 'owner', full=True)
    def dehydrate(self, bundle):
        bundle.data['id'] = str(bundle.data['id'])
        bundle.data['networks'] = [str(net.data['id']) for net in bundle.data['networks']]
        bundle.data['environment'] = [str(env.data['id']) for env in bundle.data['environment']]
        bundle.data['papers'] = [str(ref.data['id']) for ref in bundle.data['papers']]
        bundle.data['data'] = [str(ref.data['id']) for ref in bundle.data['data']]
        bundle.data['owner'] = str(bundle.data['owner'].data['username'])
        return bundle
    class Meta:
        queryset = Dataset.objects.all()
        authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication(), Authentication())
        authorization = MangalAuthorization()
        always_return_data = True
        resource_name = 'dataset'
        filtering = {
                'owner': ALL_WITH_RELATIONS,
                'networks': ALL_WITH_RELATIONS,
                'description': ALL,
                'name': ALL,
                }
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'post', 'patch', 'delete']
