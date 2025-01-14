from monithor.models import Source
from monithor.snmp import SNMP
from monithor.statusmsg import Statusmsg
from monithor.maclists import Maclists
import threading
import time

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        args[0].work = thread
        thread.start()
        return thread
    return wrapper

''' Class Engine, running the monithor backend'''
class Engine:
    def __init__(self):
        self.running = True
        self.thread = self.fetch()
        statusmsg = Statusmsg()
        maclists = Maclists()
        snmp = SNMP()

    @threaded
    def fetch(self):
        while self.running:
            ''' Handle 0 as scantime'''
            self.scantime = SNMP.get_interval()
            if self.scantime == 0:
                ''' 0 means scanning turned off '''
                Statusmsg.set_snmp_msg(" Mac scanning service turned off")
                while self.scantime == 0:
                    ''' Service turned off '''
                    self.scantime = Source.objects.first().interval_int
                    time.sleep(3)
                ''' Starting again '''
                Statusmsg.clear_snmp_msg()
            ''' Fetching macs and compare to existing'''
            Maclists.compare(SNMP.fetch_mac(SNMP.get_ip(), SNMP.get_oid(), SNMP.get_community()))


            time.sleep(self.scantime)
