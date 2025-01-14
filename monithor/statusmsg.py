from monithor.models import Status_msg

class Statusmsg:
    def __init__(self):
        if Status_msg.objects.count() < 1:
            row = Status_msg(pushover_text="", maclookup_text="",snmp_text="")
            row.save()
    @staticmethod
    def set_pushover_msg(msg):
        row = Status_msg.objects.first()
        row.pushover_text = msg
        row.save()

    @staticmethod
    def clear_pushover_msg(msg):
        row = Status_msg.objects.first()
        row.pushover_text = ""
        row.save()

    @staticmethod
    def set_maclookup_msg(msg):
        row = Status_msg.objects.first()
        row.maclookup_text = msg
        row.save()

    @staticmethod
    def clear_maclookup_msg(msg):
        row = Status_msg.objects.first()
        row.maclookup_text = ""
        row.save()

    @staticmethod
    def set_snmp_msg(msg):
        row = Status_msg.objects.first()
        row.snmp_text = msg
        row.save()

    @staticmethod
    def clear_snmp_msg():
        row = Status_msg.objects.first()
        row.snmp_text = ""
        row.save()
