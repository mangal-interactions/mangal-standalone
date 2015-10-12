from django.shortcuts import render
from django.http import HttpResponse
from test_api.models import *
from django.http import JsonResponse

def index(request):
    now = "It works!"
    html = """<html><body><h1>%s</h1>
    <p>Now, you can see the API at <code>http://localhost:8000/api/v1/?format=json</code></p>
    <p>If you use the standalone version of mangal to test the upload of your data, use <code>http://localhost:8000</code> as the
    API adress in R or python!</p>
    <p>The default user name is <code>test</code>, and the default API key is <code>9d00823baa5be60d788d079143d9785a4ffd3eec</code></p>
    </body></html>
    """ % now
    return HttpResponse(html)

def globi(request):
    interactions = Interaction.objects.all().prefetch_related()
    globi_response = []
    # Translation of mangal interactions into OBO relations
    # TODO this should have a second dict with OBO keys
    interaction_type = {
        "predation": ["eats", "RO_0002470"],
        "herbivory": ["eats", "RO_0002470"],
        "ectoparasitism": ["parasite of", "RO_0002444"],
        "endoparasitism": ["parasite of", "RO_0002444"],
        "intra-cellular parasitism": ["parasite of", "RO_0002444"],
        "parasitoidism": ["parasite of", "RO_0002444"],
        "mycoheterotrophy": ["symbiotically interacts with", "RO_0002440"],
        "antixenosis": ["biotically interacts with", "RO_0002437"],
        "teletoxy": ["biotically interacts with", "RO_0002437"],
        "amensalism": ["biotically interacts with", "RO_0002437"],
        "antibiosis": ["biotically interacts with", "RO_0002437"],
        "allelopathy": ["allelopath of", "RO_0002555"],
        "pollination": ["pollinates", "RO_0002455"],
        "mutualistic symbiosis": ["mutualistically interacts with", "RO_0002442"],
    }
    for interaction in interactions:
        proceed = True
        # Check a series of conditions
        if not interaction.link_type in interaction_type:
            proceed = False
        if proceed:
            globi_interaction_object = {}
            # Add various properties when known
            globi_interaction_object["sourceTaxonName"] = interaction.taxa_from.name
            globi_interaction_object["targetTaxonName"] = interaction.taxa_to.name
            globi_interaction_object["interactionTypeId"] = interaction_type[interaction.link_type][1]
            globi_interaction_object["interactionTypeName"] = interaction_type[interaction.link_type][0]
            # Look for lat/lon in the network object
            if not interaction.latitude is None:
                globi_interaction_object["decimalLatitude"] = interaction.latitude
            else:
                networks = interaction.network_set.all()
                if len(networks) == 1:
                    if not networks[0].latitude is None:
                        globi_interaction_object["decimalLatitude"] = networks[0].latitude
            if not interaction.longitude is None:
                globi_interaction_object["decimalLongitude"] = interaction.longitude
            else:
                networks = interaction.network_set.all()
                if len(networks) == 1:
                    if not networks[0].longitude is None:
                        globi_interaction_object["decimalLongitude"] = networks[0].longitude
            # Add everything and return
            globi_response.append(globi_interaction_object)
    return JsonResponse(globi_response, safe=False)
