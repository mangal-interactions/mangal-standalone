from django.shortcuts import render
from django.http import HttpResponse

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
