from django.contrib import admin

from lfs_forum.models import Forum, Section, Thread, Comment

admin.site.register(Forum)
admin.site.register(Section)
admin.site.register(Thread)
admin.site.register(Comment)
