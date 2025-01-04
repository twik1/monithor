from django.shortcuts import render
from monithor.models import Known_mac, Unknown_mac
from django.http import HttpResponse

def settings_view(request):
    return render(request, 'settings.html')

def index_view(request):
    kmaclist = list(Known_mac.objects.values())
    return render(request, 'index.html', {'kmaclist':kmaclist})

def unhandled_view(request):
    umaclist = list(Unknown_mac.objects.values())
    return render(request, 'unhandled.html', {'umaclist':umaclist})
