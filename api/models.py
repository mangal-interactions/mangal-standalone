from django.db import models
from django.contrib.auth.models import User

# Auto-generation of API keys

from django.contrib.auth.models import User
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

# these models are elements of the mangal data specification

M_NAME = 400
D_NAME = 1000

# reference
class Ref(models.Model):
   doi = models.CharField(max_length=200, blank=True, null=True, help_text = "DOI of the reference object")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
   jstor = models.CharField(max_length=200, blank=True, null=True, help_text = "JSTOR identifier of the reference object")
   pmid = models.CharField(max_length=200, blank=True, null=True, help_text = "PubMed ID of the reference object")
   url = models.CharField(max_length=200, blank=True, null=True, help_text = "URL of the reference object")

# environment
class Environment(models.Model):
   name = models.CharField(max_length=M_NAME, help_text = "The environmental property being measured")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
   value = models.CharField(help_text = "The value of the environmental property", max_length = 50)
   units = models.CharField(max_length=50, help_text = "The units in which the environmental property is measured", blank=True, null=True)
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A description of the environmental property")
   def __unicode__(self):
      return u'%s (%.4f %s)' % (self.name, self.value, self.units)

# trait
class Trait(models.Model):
   name = models.CharField(max_length=M_NAME, help_text  = "The name of the measured trait")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner", help_text = "The identifier of the uploader")
   value = models.CharField(help_text = "The value of the trait", max_length=50)
   units = models.CharField(max_length=50, help_text = "Units in which the trait was measured", blank=True, null=True)
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A longer description of the trait")
   latitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Latitude")
   longitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Longitude")
   environment = models.ManyToManyField(Environment,blank=True,null=True, help_text = "Local environment")
   papers = models.ManyToManyField(Ref, related_name='trait_papers',blank=True,null=True)
   data = models.ManyToManyField(Ref, related_name='trait_data',blank=True,null=True)
   date = models.DateField(blank=True, null=True, help_text="The time at which the traits were measured")
   def __unicode__(self):
       return u'%s (%.4f %s)' % (self.name, self.value, self.units)

# taxa
class Taxa(models.Model):
   TAXO_CHOICE = (
           ('confirmed', 'Confirmed'),
           ('trophic species', 'Trophic species'),
           ('morphospecies', 'Morphospecies'),
           ('nomen dubium', 'nomen dubium'),
           ('nomen oblitum', 'nomen oblitum'),
           ('nomen nudum', 'nomen nudum'),
           ('nomen novum', 'nomen novum'),
           ('nomen conservandum', 'nomen conservandum'),
           ('species inquirenda', 'species inquirenda'),
           )
   name = models.CharField(max_length=M_NAME, unique=True, help_text = "The scientific name of the taxa")
   owner = models.ForeignKey(User, related_name ="%(app_label)s_%(class)s_owner")
   vernacular = models.CharField(max_length=M_NAME, help_text = "The vernacular name of the taxa, in English", blank=True, null=True)
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A short description of the taxa")
   traits = models.ManyToManyField(Trait,blank=True,null=True)
   ncbi = models.IntegerField(blank=True,null=True, unique=True, help_text = "The NCBI Taxonomy identifier of the taxa")
   tsn = models.IntegerField(blank=True,null=True, unique=True, help_text = "The TSN identifier")
   gbif = models.IntegerField(blank=True,null=True, unique=True, help_text = "The GBIF identifier of the taxa")
   bold = models.IntegerField(blank=True,null=True, unique=True, help_text = "The BOLD identifier of the taxa")
   eol = models.IntegerField(blank=True,null=True, unique=True, help_text = "The EOL identifier of the taxa")
   status = models.CharField(max_length=50, choices = TAXO_CHOICE, default = 'confirmed', help_text = "The taxonomic status of the taxa.")
   def __unicode__(self):
       na = self.name
       if self.vernacular > 0:
           na += " ("+self.vernacular+")"
       return na

# item
class Item(models.Model):
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner", help_text = "The identifier of the uploader")
   taxa = models.ForeignKey(Taxa)
   level = models.CharField(max_length=50, choices = (('individual', 'Individual'), ('population', 'Population'),), help_text = "Whether the item is a single individual, or a population")
   name = models.CharField(max_length=M_NAME, help_text = "A name for the item, useful to identify it later")
   traits = models.ManyToManyField(Trait,blank=True,null=True)
   size = models.FloatField(blank=True,null=True, help_text = "If the item is a population, the number of individuals or biomass")
   units = models.CharField(max_length=50,blank=True,null=True, help_text = "Units in which the population size is measured")
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A short description of the population")
   def __unicode__(self):
       return u'%s (%s) - belongs to %s' % (self.name, self.level, self.taxa)

# interaction
class Interaction(models.Model):
   STAGE_CHOICES = (
           ('seed', 'Seed'),
           ('juvenile', 'Juvenile'),
           ('adult', 'Adult'),
           ('dead', 'Dead'),
           ('larva', 'Larva'),
           ('all', 'All'),
           )
   TYPE_CHOICES = (
           ('predation', 'Predation'),
           ('herbivory', 'Herbivory'),
           ('ectoparasitism', 'Ectoparasitism'),
           ('endoparasitism', 'Endoparasitism'),
           ('intra-cellular parasitism', 'Intra-Cellular parasitism'),
           ('parasitoidism', 'Parasitoidism'),
           ('mycoheterotrophy', 'Mycoheterotrophy'),
           ('antixenosis', 'Anitxenosis'),
           ('teletoxy', 'Teletoxy'),
           ('amensalism', 'Amensalism'),
           ('antibiosis', 'Antibiosis'),
           ('allelopathy', 'Allelopathy'),
           ('competition', 'Competition'),
           ('facilitation', 'Facilitation'),
           ('refuge creation', 'Refuge creation'),
           ('inquilinism', 'Inquilinism'),
           ('phoresis', 'Phoresis'),
           ('epibiosis', 'Epibiosis'),
           ('pollination', 'Pollination'),
           ('mutualistic symbiosis', 'Mutualistic symbiosis'),
           ('zoochory', 'Zoochory'),
           ('mutual protection', 'Mutual protection'),
        )
   SEX_CHOICES = (
           ('all', 'All'),
           ('male', 'Male'),
           ('female', 'Female'),
           ('unknown', 'Unknown'),
           )
   OBSERVATION_CHOICES = (
           ('unspecified', 'Unspecified'),
           ('observation', 'Observation'),
           ('litterature', 'Litterature'),
           ('absence', 'Confirmed absence'),
           ('inferred', 'Inferred'),
           )
   public = models.BooleanField(default=True, blank=True, help_text="Whether the interaction can be viewed by all users")
   link_type = models.CharField(max_length=50, choices = TYPE_CHOICES, help_text  ="The type of interaction")
   obs_type = models.CharField(max_length=50, choices = OBSERVATION_CHOICES, help_text  ="How the interaction was observed")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
   taxa_from = models.ForeignKey(Taxa, related_name='taxa_from')
   taxa_to = models.ForeignKey(Taxa, related_name='taxa_to')
   item_from = models.ForeignKey(Item, related_name='item_from', blank=True, null=True)
   item_to = models.ForeignKey(Item, related_name='item_to', blank=True, null=True)
   stage_from = models.CharField(max_length=50, choices = STAGE_CHOICES, default = 'all', help_text = "The stage of the establishing entity, to be selected in the list of allowed values")
   stage_to = models.CharField(max_length=50, choices = STAGE_CHOICES, default = 'all', help_text = "The stage of the receiving entity, to be selected in the list of allowed values")
   sex_from = models.CharField(max_length=50, choices = SEX_CHOICES, default = 'all', help_text = "The sex of the establishing, to be selected in the list of allowed values")
   sex_to = models.CharField(max_length=50, choices = SEX_CHOICES, default = 'all', help_text = "The sex of the receiving entity, to be selected in the list of allowed values")
   strength_f = models.FloatField(blank=True,null=True, help_text = "The strength of the interaction for the item ESTABLISHING the interaction")
   strength_t = models.FloatField(blank=True,null=True, help_text = "The strength of the interaction for the item RECEVING the interaction")
   units_f = models.CharField(max_length=50,blank=True,null=True, help_text = "Units in which the interaction strength is measured")
   units_t = models.CharField(max_length=50,blank=True,null=True, help_text = "Units in which the interaction strength is measured")
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A description of the interaction")
   latitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Latitude")
   longitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Longitude")
   environment = models.ManyToManyField(Environment,blank=True,null=True, help_text = "Local environment")
   papers = models.ManyToManyField(Ref, related_name='int_papers',blank=True,null=True)
   data = models.ManyToManyField(Ref, related_name='int_data',blank=True,null=True)
   date = models.DateField(blank=True, null=True, help_text="The time at which the interaction was sampled")
   def __unicode__(self):
       From = self.taxa_from
       To = self.taxa_to
       if self.item_from :
          From = self.item_from
       if self.item_to:
          To = self.item_to
       return u'%s (%s) of %s by %s'% (self.link_type, self.obs_type, To, From)


# network
class Network(models.Model):
   public = models.BooleanField(default=True, blank=True, help_text="Whether the network can be viewed by all users")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
   name = models.CharField(max_length=M_NAME, help_text = "The name of the network")
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A short description of the network")
   interactions = models.ManyToManyField(Interaction)
   latitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Latitude")
   longitude = models.CharField(max_length=20,blank=True,null=True, help_text = "Longitude")
   environment = models.ManyToManyField(Environment,blank=True,null=True)
   papers = models.ManyToManyField(Ref, related_name='net_papers',blank=True,null=True)
   data = models.ManyToManyField(Ref, related_name='net_data',blank=True,null=True)
   date = models.DateField(blank=True, null=True, help_text="The time at which the network was sampled")
   def __unicode__(self):
       return self.name

# dataset
class Dataset(models.Model):
   public = models.BooleanField(default=True, blank=True, help_text="Whether the dataset can be viewed by all users")
   owner = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_owner")
   name = models.CharField(max_length=M_NAME, help_text = "The name of the dataset")
   description = models.CharField(max_length=D_NAME,blank=True,null=True, help_text = "A short description of the dataset")
   papers = models.ManyToManyField(Ref, related_name='papers',blank=True,null=True)
   data = models.ManyToManyField(Ref, related_name='data',blank=True,null=True)
   networks = models.ManyToManyField(Network, blank=True,null=True, related_name='network')
   environment = models.ManyToManyField(Environment,blank=True,null=True)
   def __unicode__(self):
       return self.name
