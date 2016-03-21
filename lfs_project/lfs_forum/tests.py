from django.test import TestCase, Client
from django.contrib.auth.models import User
from lfs_forum.models import Forum, Section, Thread, Comment

import datetime

class ForumAppTests(TestCase):

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user("jdoe",
                                             "jdoe@gmail.com",
                                             "123",
                                             first_name="John",
                                             last_name="Doe")
        
        self.forum = Forum.objects.create(title="Forum")
        self.section = Section.objects.create(forum=self.forum,
                                              title="Section")
        self.thread = Thread.objects.create(section=self.section,
                                            user=self.user,
                                            title="Thread")
        
    def test_forum_model(self):
        forum = Forum.objects.create(title="NewForum")

        self.assertEqual(str(forum), forum.title)

        
    def test_forum_section(self):
        sec = Section.objects.create(forum=self.forum,
                                     title="NewSection")

        self.assertEqual(str(sec), sec.title)


    def test_forum_thread(self):
        thread = Thread.objects.create(section=self.section,
                                       user=self.user,
                                       title="NewThread")

        self.assertEqual(str(thread), thread.title)


    def test_forum_comment(self):
        comm = Comment.objects.create(thread=self.thread,
                                      user=self.user,
                                      time=datetime.datetime.now(),
                                      content="Random stuff")

        self.assertEqual(str(comm),
                         "Comment for {0}".format(str(self.thread)))
