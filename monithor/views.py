from django.shortcuts import render
from django.forms.models import model_to_dict
from monithor.models import Known_mac, Unknown_mac, Source, Notification, Macinfo
import json
from django.http import HttpResponse

def settings_view(request):
    valuedict = {}

    if request.method == 'POST':
        data = request.POST
        if 'snmp_address' in data:
            if Source.objects.count() < 1:
                row = Source(ip_text=data['snmp_address'], oid_text=data['oid'], interval_int=int(data['interval']))
                row.save()
            else:
                row = Source.objects.first()
                row.ip_text = data['snmp_address']
                row.oid_text = data['oid']
                row.interval_int = int(data['interval'])
                row.save()
        if 'apikey' in data:
            if Macinfo.objects.count() < 1:
                row = Macinfo(token_mac_text=data['apikey'])
                row.save()
            else:
                row = Macinfo.objects.first()
                row.token_mac_text = data['apikey']
                row.save()
        if 'token' in data:
            if Notification.objects.count() < 1:
                row = Notification(token_text=data['token'], user_text=data['user'])
                row.save()
            else:
                row = Notification.objects.first()
                row.token_text = data['token']
                row.user_text = data['user']
                row.save()

    '''Make sure we handle an empty database'''
    if Source.objects.count() < 1:
        dsource = {'ip_text':'', 'oid_text':'', 'interval_int':0}
    else:
        dsource = model_to_dict(Source.objects.first())

    if Notification.objects.count() < 1:
        dnotifi = {'token_text':'', 'user_text':''}
    else:
        dnotifi = model_to_dict(Notification.objects.first())

    if Macinfo.objects.count() < 1:
        dmacinf = {'token_mac_text':''}
    else:
        dmacinf = model_to_dict(Macinfo.objects.first())
    valuedict = {**dsource, **dnotifi, **dmacinf}

    return render(request, 'settings.html', {'source':valuedict})

def about_view(request):
    return render(request, 'about.html')

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
