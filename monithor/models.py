from django.db import models

class Notification(models.Model):
    token_text = models.CharField(max_length=50)
    user_text = models.CharField(max_length=50)
    def __str__(self):
        return (self.token_text, self.user_text)

class Macinfo(models.Model):
    token_mac_text = models.CharField(max_length=256)

class Source(models.Model):
    ip_text = models.CharField(max_length=20)
    oid_text = models.CharField(max_length=150)
    community_text = models.CharField(max_length=50)
    interval_int = models.IntegerField(default=0)
    def __str__(self):
        return (self.ip_text, self.oid_text)

class Maclist(models.Model):
    mac_text = models.CharField(max_length=20)
    mac_inf_text = models.CharField(max_length=100)
    device_text = models.CharField(max_length=100)
    count_int = models.IntegerField(default=0)
    first_seen_date = models.DateTimeField("first seen")
    last_seen_date = models.DateTimeField("last seen")
    type_int = models.IntegerField(default=0)
    def __str__(self):
        return (self.mac_text)

class Status_msg(models.Model):
    pushover_text = models.CharField(max_length=256)
    maclookup_text = models.CharField(max_length=256)
    snmp_text = models.CharField(max_length=256)
    def __str__(self):
        return (self.snmp_text)
