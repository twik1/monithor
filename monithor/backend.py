import time
import re
import http.client
import urllib
import easysnmp.exceptions
from easysnmp import Session, EasySNMPTimeoutError, EasySNMPUnknownObjectIDError, EasySNMPNoSuchInstanceError
import threading
import argparse
import datetime

from monithor.models import Known_mac, Unknown_mac, Macinfo, Source, Notification, Status_msg
import requests
from django.utils import timezone

def pushover_send(msg):
    print("tesssst")
    notify = Status_msg.objects.first()
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
            notify.pushover_text = "Pushover failed with HTTP response {}".format(res.status)
        else:
            notify.pushover_text = ""
    except Exception as e:
        print("failed")
        notify.pushover_text = "Pushover failed {}".format(e)
    notify.save()


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        # print('spwaning thred:{}'.format(thread))
        args[0].work = thread
        thread.start()
        return thread
    return wrapper

#Todo use a baseclass and inherit
class Kmac:
    def __init__(self):
        self.pdict = {}

    def set(self, list1):
        for value in list1:
            row = Known_mac.objects.get(mac_text=value['mac_text'])
            print(row.count_int)
            self.pdict[value['mac_text']] = row.count_int

    def update(self, list1):
        #update the once that are present
        retlist = []
        for value in list1:
            if value in self.pdict:
                if self.pdict[value] < 1:
                    print('{} present'.format(value))
                    row = Known_mac.objects.get(mac_text=value)
                    row.last_seen_date = timezone.now()
                    row.count_int = 3
                    row.save()
                self.pdict[value] = 3
                retval = True
            else:
                retlist.append(value)
        #decrement the once that are not present
        for key in list(self.pdict.keys()):
            if key not in list1:
                if self.pdict[key] == 0:
                    continue
                if self.pdict[key] == 1:
                    print('{} removed'.format(key))
                    self.pdict[key] = 0
                    row = Known_mac.objects.get(mac_text=key)
                    row.count = 0
                    row.save()
                if self.pdict[key] > 1:
                    print('{} decremented'.format(key))
                    self.pdict[key] -= 1
        return retlist

class Umac:
    def __init__(self):
        self.plist = []

    @classmethod
    def get_info_of_mac(self, mac):
        msg = Status_msg.objects.first()
        try:
            ret = requests.get(
                'https://api.maclookup.app/v2/macs/{}?apiKey={}'.format(mac, Macinfo.objects.first().token_mac_text))
            print(ret.json())
            if ret.json()['success']:
                if ret.json()['found']:
                    macinfo = ret.json()['company']
                else:
                    macinfo = 'Not found'
                msg.maclookup_text = ""
            else:
                macinfo = 'Failed'
                msg.maclookup_text = "Maclookup request failed: {}".format(ret.json()['error'])
        except Exception as e:
            macinfo = 'Failed'
            msg.maclookup_text = "Maclookup request failed {}".format(e)
        msg.save()
        return macinfo

    def set(self, list1):
        for row in list1:
            self.plist.append(row['mac_text'])
        print(self.plist)

    def update(self, list1):
        retlist = []
        for value in list1:
            if value in self.plist:
                row = Unknown_mac.objects.get(mac_text=value)
                row.last_seen_date = timezone.now()
                row.save()
            else:
                retlist.append(value)
                macinfo = self.get_info_of_mac(value)
                row = Unknown_mac(mac_text=value, mac_inf_text=macinfo, first_seen_date=timezone.now(), last_seen_date=timezone.now())
                row.save()
                print('Adding mac to db {}'.format(value))
                self.plist.append(value)
        return retlist

class SNMP:
    def __init__(self):
        self.running = True
        self.cmaclist = []
        self.cdmaclist = {}
        ''' Deal with an empty database '''
        if Source.objects.count() < 1:
            dsource = {'ip_text': '', 'oid_text': '', 'interval_int': 0, 'community_text': ''}
            row = Source(ip_text=dsource['ip_text'], oid_text=dsource['oid_text'], interval_int=dsource['interval_int'],
                         community_text=dsource['community_text'])
            row.save()

        if Notification.objects.count() < 1:
            dnotifi = {'token_text': '', 'user_text': ''}
            row = Notification(token_text=dnotifi['token_text'], user_text=dnotifi['user_text'])
            row.save()

        if Macinfo.objects.count() < 1:
            dmacinf = {'token_mac_text': ''}
            row = Macinfo(token_mac_text=dmacinf['token_mac_text'])
            row.save()

        if Status_msg.objects.count() < 1:
            status = {'pushover_text': '', 'maclookup_text': '', 'snmp_text': ''}
            row = Status_msg(pushover_text=status['pushover_text'], maclookup_text=status['maclookup_text'],
                             snmp_text=status['snmp_text'])
            row.save()

        self.scantime = Source.objects.first().interval_int
        self.thread = self.fetch()

    def format(self, macstring):
        return ':'.join(a + b for a, b in zip(macstring[::2], macstring[1::2]))

    def validate(self, macstring):
        if macstring == '000000000000':
            print('False mac 1')
            return False
        if macstring == 'ffffffffffff':
            print('False mac 2')
            return False
        if (int(macstring[:2], 16) % 2):
            print('False mac 3')
            return False
        return True


    def fetch_mac(self):
        ''' We should not fetch if function turned off '''
        if Source.objects.first().interval_int == 0:
            msg = Status_msg.objects.first()
            msg.snmp_text = "Fetching mac address turned off"
            msg.save()
            return []

        ''' Need special treatment since it terminates if parameters are wrong'''
        ipv4re = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        oidre = re.compile("^\..*\d{1,3}$")

        ipaddress = Source.objects.first().ip_text
        oid = Source.objects.first().oid_text
        community = Source.objects.first().community_text
        msg = Status_msg.objects.first()
        res = []
        if not ipv4re.match(ipaddress):
            msg.snmp_text = "Ip-address v4 failed validation {}".format(ipaddress)
        elif not oidre.match(oid):
            msg.snmp_text = "OID failed validation {}".format(oid)
        else:
            session =  Session(hostname=ipaddress, community=community, timeout=1, version=2, retries=3)
            try:
                res = session.walk(oid)
                msg.snmp_text = ""
            except easysnmp.exceptions.EasySNMPTimeoutError:
                msg.snmp_text = "SNMP timeout"
            except easysnmp.exceptions.EasySNMPError:
                msg.snmp_text = "SNMP error"
        msg.save()
        return res

    @threaded
    def fetch(self):
        newmac = []
        leftover1 = []
        kmac = Kmac()
        umac = Umac()
        kmac.set(list(Known_mac.objects.values()))
        umac.set(list(Unknown_mac.objects.values()))
        #oid = ['.1.3.6.1.2.1.4.22.1.2']
        while self.running:
            scanned_maclist = []
            res = self.fetch_mac()
            for row in res:
                if self.validate(row.value.encode('latin-1').hex()):
                    scanned_maclist.append(self.format(row.value.encode('latin-1').hex()))
            leftover1 = kmac.update(scanned_maclist)
            newmac = umac.update(leftover1)
            #print(':{}:'.format(newmac))
            #pushover_send('Warning an unknown mac has joined the network {}'.format(mac))

            ''' Handle 0 as scantime'''
            self.scantime = Source.objects.first().interval_int
            print("scantime:{}".format(self.scantime))
            if self.scantime == 0:
                ''' 0 means scanning turned off '''
                msg = Status_msg.objects.first()
                msg.snmp_text = "Fetching mac address turned off"
                msg.save()
                while self.scantime == 0:
                    ''' Service turned off '''
                    self.scantime = Source.objects.first().interval_int
                    time.sleep(3)
                ''' Starting again '''
                msg = Status_msg.objects.first()
                msg.snmp_text = ""
                msg.save()
            time.sleep(self.scantime)

    def join(self):
        self.thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='monithor v0.1')
    parser.add_argument('-s', '--scan', help='Which interval (sec) to scan the router for macs', required=True)
    args = parser.parse_args()

    snmp = SNMP(30)
    snmp.join()
