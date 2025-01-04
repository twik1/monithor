from django.shortcuts import render
from monithor.models import Known_mac, Unknown_mac
import json
from django.http import HttpResponse

def settings_view(request):
    return render(request, 'settings.html')

def index_view(request):
    kmaclist = list(Known_mac.objects.values())
    return render(request, 'index.html', {'kmaclist':kmaclist})

def unhandled_view(request):
    if request.method == 'POST':
        data = request.POST
        notes = data['notes']
        id = data['id']
        #ToDo Add fault handling
        row = Unknown_mac.objects.get(id=int(id))
        irow = Known_mac(mac_text=row.mac_text, mac_inf_text=row.mac_inf_text, first_seen_date=row.first_seen_date,
                  last_seen_date=row.last_seen_date, device_text=notes)
        irow.save()
        Unknown_mac.objects.filter(id=int(id)).delete()
    umaclist = list(Unknown_mac.objects.values())
    return render(request, 'unhandled.html', {'umaclist':umaclist})
