from monithor.models import Source
from monithor.statusmsg import Statusmsg
from easysnmp import Session, EasySNMPTimeoutError, EasySNMPError
import re

class SNMP:
    def __init__(self):
        if Source.objects.count() < 1:
            dsource = {'ip_text': '', 'oid_text': '', 'interval_int': 0, 'community_text': ''}
            row = Source(ip_text=dsource['ip_text'], oid_text=dsource['oid_text'], interval_int=dsource['interval_int'],
                         community_text=dsource['community_text'])
            row.save()
        #SNMP.set_interval(10)

    @staticmethod
    def set_ip(ip):
        row = Source.objects.first()
        row.ip_text = ip
        row.save()

    @staticmethod
    def get_ip():
        row = Source.objects.first()
        return row.ip_text

    @staticmethod
    def set_oid(oid):
        row = Source.objects.first()
        row.oid_text = oid
        row.save()

    @staticmethod
    def get_oid():
        row = Source.objects.first()
        return row.oid_text

    @staticmethod
    def set_community(community):
        row = Source.objects.first()
        row.community_text = community
        row.save()

    @staticmethod
    def get_community():
        row = Source.objects.first()
        return row.community_text

    @staticmethod
    def set_interval(interval):
        row = Source.objects.first()
        row.interval_int = interval
        row.save()

    @staticmethod
    def get_interval():
        row = Source.objects.first()
        return row.interval_int

    @staticmethod
    def fetch_mac(ip, oid, community):
        ''' We should not fetch if function turned off '''
        if SNMP.get_interval() == 0:
            Statusmsg.set_snmp_msg("Fetching mac address turned off")
            return []
        scanned_maclist = []
        ''' Need special treatment since it terminates if parameters are wrong'''
        ipv4re = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        oidre = re.compile("^\..*\d{1,3}$")

        ipaddress = SNMP.get_ip()
        oid = SNMP.get_oid()
        community = SNMP.get_community()
        res = []
        if not ipv4re.match(ipaddress):
            Statusmsg.set_snmp_msg("Ip-address v4 failed validation {}".format(ipaddress))
        elif not oidre.match(oid):
            Statusmsg.set_snmp_msg("OID failed validation {}".format(oid))
        else:
            session =  Session(hostname=ipaddress, community=community, timeout=1, version=2, retries=3)
            try:
                res = session.walk(oid)
                Statusmsg.clear_snmp_msg()
            except EasySNMPTimeoutError:
                Statusmsg.set_snmp_msg("SNMP timeout")
            except EasySNMPError:
                Statusmsg.set_snmp_msg("SNMP error")
        for row in res:
            if SNMP.validate(row.value.encode('latin-1').hex()):
                scanned_maclist.append(SNMP.format(row.value.encode('latin-1').hex()))
        return scanned_maclist

    @staticmethod
    def format(macstring):
        return ':'.join(a + b for a, b in zip(macstring[::2], macstring[1::2]))

    @staticmethod
    def validate(macstring):
        if macstring == '000000000000':
            return False
        if macstring == 'ffffffffffff':
            return False
        if (int(macstring[:2], 16) % 2):
            return False
        return True
