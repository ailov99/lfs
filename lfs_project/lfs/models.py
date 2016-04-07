from __future__ import unicode_literals
import os

from django.db import models
from django.contrib.auth.models import User
from hitcount.models import HitCountMixin


class Teacher(models.Model):
    """ Representing teacher in database, subclass of User. """
    user = models.OneToOneField(User)

    # Additional fields to save more info about teacher
    bio = models.CharField(max_length=500, default='')
    school = models.CharField(max_length=200, default='')
    AGE_RANGE_CHOICES = (
        ('0', '16-21'),
        ('1', '22-28'),
        ('2', '29-35'),
        ('3', '36-42'),
        ('4', '42-48'),
        ('5', '49-55'),
        ('6', '56 or older'),
    )
    age_range = models.CharField(max_length=2,
                                 choices=AGE_RANGE_CHOICES,
                                 default='0')
    location = models.CharField(max_length=200, default='')
    picture = models.ImageField(upload_to='static/Pictures/', blank=True)
    # opt in to leaderboard
    leaderboard = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.username


class Module(models.Model, HitCountMixin):
    """ Representing modules, have many to many relationship with teachers,
        this relationship is expressed through Takers class, so it's possible
        to save progress for action """
    taker = models.ManyToManyField(User, through='Takers')

    title = models.CharField(max_length=200)
    background = models.ImageField(upload_to='static/Pictures/', blank=True)
    # downloadable = models.FileField(upload_to='Content/', blank=True)

    trial = models.BooleanField(default=False)
    compulsory = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class ContentFile(models.Model):
    """ Represents a downloadable file """
    module = models.ForeignKey(Module)
    file = models.FileField(upload_to='Content/', blank=True)
    clicks = models.IntegerField(default=0)

    def filename(self):
        return os.path.basename(self.file.name)


class Takers(models.Model):
    """ Many to many representation between Modules and Teachers. """
    user = models.ForeignKey(User)
    module = models.ForeignKey(Module)

    progress = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.username + self.module.title


class Page(models.Model):
    module = models.ForeignKey(Module)

    position = models.IntegerField(default=0)  # order of page
    section = models.CharField(max_length=200)  # title of section
    content = models.TextField()

    # Maintain table order by insertion time
    time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['time']

    def __unicode__(self):
        return self.section


# Workaround to storing dictionaries as fields

class ModuleVideo(models.Model):
    module = models.ForeignKey(Module)

    video = models.FileField(upload_to='ModuleVideos/')


class PageVideo(models.Model):
    page = models.ForeignKey(Page)

    video = models.FileField(upload_to='PageVideos/')


class Picture(models.Model):
    page = models.ForeignKey(Page)

    picture = models.ImageField(upload_to='Pictures/', blank=True)
