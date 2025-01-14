from monithor.statusmsg import Statusmsg
from monithor.models import Maclist, Macinfo, Notification
from django.utils import timezone
import requests
import http.client
import urllib

UNKNOWN_MAC = 0
KNOWN_MAC = 1

''' Class deling with the mac models, both Known and Unknown '''
class Maclists:
    def __init__(self):
        if Notification.objects.count() < 1:
            row = Notification(token_text="", user_text="")
            row.save()
        if Macinfo.objects.count() < 1:
            row = Macinfo(token_mac_text="")
            row.save()

    @staticmethod
    def add_mac(mac, macinfo, device, type):
        if type == UNKNOWN_MAC:
            macinfo = Maclists.get_info_of_mac(mac)
        row = Maclist(mac_text=mac, mac_inf_text=macinfo, device_text=device, count_int=0,
                first_seen_date=timezone.now(), last_seen_date=timezone.now(), type_int=type)
        row.save()

    @staticmethod
    def change_to_known(id, device):
        row = Maclist.objects.get(id=id)
        row.device_text = device
        row.type_int = KNOWN_MAC
        row.save()

    @staticmethod
    def get_counter(mac):
        row = Maclist.objects.get(mac_text=mac)
        return row.count_int

    @staticmethod
    def set_counter(mac, count):
        row = Maclist.objects.get(mac_text=mac)
        row.count_int = count
        row.save()

    @staticmethod
    def clear_counter(mac):
        row = Maclist.objects.get(mac_text=mac)
        row.count_int = 0
        row.save()

    @staticmethod
    def update_last_seen(mac):
        row = Maclist.objects.get(mac_text=mac)
        row.last_seen_date = timezone.now()
        row.save()

    @staticmethod
    def get_unknown():
        return list(Maclist.objects.filter(type_int=UNKNOWN_MAC))

    @staticmethod
    def get_known():
        return list(Maclist.objects.filter(type_int=KNOWN_MAC))

    @staticmethod
    def pushover_send(msg):
        try:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
                         urllib.parse.urlencode({
                             "token": Notification.objects.first().token_text,
                             "user": Notification.objects.first().user_text,
                             "message": msg,
                         }), {"Content-type": "application/x-www-form-urlencoded"})
            res = conn.getresponse()
            if res.status != 200:
                Statusmsg.set_pushover_msg("Pushover failed with HTTP response {}".format(res.status))
            else:
                Statusmsg.set_pushover_msg("")
        except Exception as e:
            Statusmsg.set_pushover_msg("Pushover failed {}".format(e))


    @staticmethod
    def get_info_of_mac(mac):
        try:
            ret = requests.get(
                'https://api.maclookup.app/v2/macs/{}?apiKey={}'.format(mac, Macinfo.objects.first().token_mac_text))
            if ret.json()['success']:
                if ret.json()['found']:
                    macinfo = ret.json()['company']
                else:
                    macinfo = 'Not found'
                Statusmsg.clear_maclookup_msg()
            else:
                macinfo = 'Failed'
                Statusmsg.set_maclookup_msg("Maclookup request failed: {}".format(ret.json()['error']))
        except Exception as e:
            macinfo = 'Failed'
            Statusmsg.set_maclookup_msg("Maclookup request failed {}".format(e))
        return macinfo

    @staticmethod
    def compare(maclist):
        ''' Start comparing with the known macs '''
        leftover = []
        known = Maclists.get_known()
        unknown = Maclists.get_unknown()
        tempmac = ''
        for mac in maclist:
            for item in known:
                if item.mac_text == mac:
                    Maclists.update_last_seen(mac)
                    Maclists.set_counter(mac, 3)
                    tempmac = mac
                    continue
            if not tempmac:
                leftover.append(mac)
            tempmac = ''
        for mac in leftover:
            for item in unknown:
                if item.mac_text == mac:
                    Maclists.update_last_seen(mac)
                    tempmac = mac
                    continue
            if not tempmac:
                Maclists.add_mac(mac, "", "", UNKNOWN_MAC)

