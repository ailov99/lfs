from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Forum(models.Model):
    """Representing forum in database """
    title = models.CharField(max_length=128)

    def __unicode__(self):
        return self.title


class Section(models.Model):
    """Representing sections in database, have one to many relationships with
        forum, saves the title of the section. """
    forum = models.ForeignKey(Forum)

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class Thread(models.Model):
    """Representing threads in database, have one to many relationships with
        section and user, only have field title. """
    section = models.ForeignKey(Section)
    user = models.ForeignKey(User)

    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title


class Comment(models.Model):
    """Representing comments in database, have one to many relationships with
        thread and user, saves time when it was created and content. """
    thread = models.ForeignKey(Thread)
    user = models.ForeignKey(User)

    time = models.DateTimeField()
    content = models.TextField()

    def __unicode__(self):
        return "Comment for " + self.thread.title
