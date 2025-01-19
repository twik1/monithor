from django.shortcuts import render
from django.forms.models import model_to_dict
from monithor.maclists import Maclists
from monithor.models import Maclist, Source, Notification, Macinfo, Status_msg
from monithor.snmp import SNMP


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
            SNMP.fetch_mac(SNMP.get_ip(), SNMP.get_oid(), SNMP.get_community())
        if 'apikey' in data:
            row = Macinfo.objects.first()
            row.token_mac_text = data['apikey']
            row.save()
            Maclists.get_info_of_mac('5c:aa:fd:9f:b1:38')
        if 'token' in data:
            print(data)
            row = Notification.objects.first()
            row.token_text = data['token']
            row.user_text = data['user']
            if 'sendpush' in data:
                row.send_bool = True
            else:
                row.send_bool = False
            row.save()
            Maclists.pushover_send("Config test")
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
    kmaclist = list(Maclists.get_known())
    return render(request, 'index.html', {'kmaclist':kmaclist})

def unhandled_view(request):
    if request.method == 'POST':
        data = request.POST
        notes = data['notes']
        id = data['id']
        #ToDo Add fault handling
        Maclists.change_to_known(id, notes)
    umaclist = list(Maclists.get_unknown())
    return render(request, 'unhandled.html', {'umaclist':umaclist})
