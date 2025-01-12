from django.shortcuts import render
from django.forms.models import model_to_dict

from monithor.backend import Umac, pushover_send
from monithor.models import Known_mac, Unknown_mac, Source, Notification, Macinfo, Status_msg
from monithorsite.wsgi import snmp


def settings_view(request):
    valuedict = {}

    if request.method == 'POST':
        data = request.POST
        if 'snmp_address' in data:
            row = Source.objects.first()
            row.ip_text = data['snmp_address']
            row.oid_text = data['oid']
            row.community_text = data['community']
            row.interval_int = int(data['interval'])
            row.save()
            snmp.fetch_mac()
        if 'apikey' in data:
            row = Macinfo.objects.first()
            row.token_mac_text = data['apikey']
            row.save()
            Umac.get_info_of_mac('5c:aa:fd:9f:b1:38')
        if 'token' in data:
            print(data)
            row = Notification.objects.first()
            row.token_text = data['token']
            row.user_text = data['user']
            row.save()
            pushover_send('test')
        # ToDo test the setting before reloading the page

    dsource = model_to_dict(Source.objects.first())
    dnotifi = model_to_dict(Notification.objects.first())
    dmacinf = model_to_dict(Macinfo.objects.first())
    dstatus = model_to_dict(Status_msg.objects.first())
    valuedict = {**dsource, **dnotifi, **dmacinf, **dstatus}

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
