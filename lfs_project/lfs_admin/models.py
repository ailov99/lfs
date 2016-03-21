from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from hitcount.models import HitCountMixin

from datetime import date

class Administrator(models.Model):
    """ Admin representation in database, subclass of User """
    user = models.OneToOneField(User)

    bio = models.CharField(max_length=500)

    def __unicode__(self):
        return self.user.username

class UserRegistrations(models.Model, HitCountMixin):
    """ 
    Makeshift model for tracking user registrations
    NOTE: this is an ugly hack to reduce complexity of using
    a separate app just for user registration stats
    """
    time = models.DateField(default=date.today)
    count = models.IntegerField(default=0)

    def inc(self):
        self.count = self.count + 1
        self.save()
    
    def __unicode__(self):
        return str(self.time)

class AnonHits(models.Model, HitCountMixin):
    """
    Model for tracking anonymous visits of the welcome page
    """
    time = models.DateField(default=date.today)
    count = models.IntegerField(default=0)

    def inc(self):
        self.count = self.count + 1
        self.save()

    def __unicode__(self):
        return str(self.time)
