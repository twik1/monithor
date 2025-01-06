import time
import re
import http.client
import urllib
import easysnmp.exceptions
from easysnmp import Session, EasySNMPTimeoutError, EasySNMPUnknownObjectIDError, EasySNMPNoSuchInstanceError
import threading
import argparse
import datetime
from monithor.models import Known_mac, Unknown_mac, Macinfo, Source, Notification
import requests
from django.utils import timezone

def pushover_send(msg):
    try:
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                 urllib.parse.urlencode({
                     "token": Notification.objects.first().token_text,
                     "user": Notification.objects.first().user_text,
                     "message": msg,
                 }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()
    except Exception as e:
        print('pushover failed {}'.format(e))


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

    def get_info_of_mac(self, mac):
        try:
            ret = requests.get(
                'https://api.maclookup.app/v2/macs/{}?apiKey={}'.format(mac, Macinfo.objects.first().token_mac_text))
            if ret.json()['success']:
                if ret.json()['found']:
                    macinfo = ret.json()['company']
                else:
                    macinfo = 'Not found'
            else:
                macinfo = 'Request failed1'
        except Exception as e:
            print(e)
            macinfo = 'Request failed2'
        return macinfo
        #row = Unknown_mac(mac_text=mac, mac_inf_text=macinfo, first_seen_date=timezone.now(),
                          #last_seen_date=timezone.now())
        #row.save()
        #print('Warning an unknown mac has joined the network {}, {}'.format(mac, macinfo))

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
    def __init__(self, scantime):
        self.running = True
        self.scantime = scantime
        self.cmaclist = []
        self.cdmaclist = {}
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

    def comp_lists(self, list1, list2):
        only_list1 = []
        only_list2 = []
        for item in list1:
            if not item in list2:
                only_list1.append(item)
        for item in list2:
            if not item in list1:
                only_list2.append(item)
        return(only_list1, only_list2)

    def comp_dict_list(self, dict1, list2, mode):
        dellist = []
        for key in dict1:
            if not key in list2:
                if dict1[key] < 1:
                    dellist.append(key)
                else:
                    dict1[key] -= 1
                    #print('{} has been decremented'.format(key))
            else:
                dict1[key] = 3
                #print('{} has been updated'.format(key))
        for entry in list2:
            if not entry in dict1 and mode:
                dict1[entry] = 3
                # Update db with present
                print('{} has been added, {}'.format(entry, datetime.datetime.now()))
        for key in dellist:
            del dict1[entry]
            # Update db with removed
            print('{} has been removed, {}'.format(entry, datetime.datetime.now()))
        return dict1

    def list_conv(self, db_result):
        clist = []
        for row in db_result:
            clist.append(row['mac_text'])
        return clist

    @threaded
    def fetch(self):
        newmac = []
        leftover1 = []
        oid = []
        kmac = Kmac()
        umac = Umac()
        kmac.set(list(Known_mac.objects.values()))
        umac.set(list(Unknown_mac.objects.values()))
        #oid = ['.1.3.6.1.2.1.4.35.1.4']
        #oid = ['.1.3.6.1.2.1.4.22.1.2']
        oid.append(Source.objects.first().oid_text)
        session = Session(hostname=Source.objects.first().ip_text, community='public', timeout=1, version=2, retries=3)
        while self.running:
            print('scanning...')
            scanned_maclist = []
            try:
                res = session.walk(oid)
            except easysnmp.exceptions.EasySNMPTimeoutError:
                print('SNMP timeout')
                continue
            except easysnmp.exceptions.EasySNMPError:
                print('SNMP error')
                continue
            # scanned_maclist is the list of the mac address found at a single scanning
            for row in res:
                if self.validate(row.value.encode('latin-1').hex()):
                    scanned_maclist.append(self.format(row.value.encode('latin-1').hex()))
            print(scanned_maclist)
            leftover1 = kmac.update(scanned_maclist)
            newmac = umac.update(leftover1)
            #print(':{}:'.format(newmac))
            #pushover_send('Warning an unknown mac has joined the network {}'.format(mac))

            time.sleep(self.scantime)

    def join(self):
        self.thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='monithor v0.1')
    parser.add_argument('-s', '--scan', help='Which interval (sec) to scan the router for macs', required=True)
    args = parser.parse_args()

    snmp = SNMP(30)
    snmp.join()
