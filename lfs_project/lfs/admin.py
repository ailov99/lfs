from django.contrib import admin

from lfs.models import Teacher, Module, Takers, Page, \
    ModuleVideo, PageVideo, Picture

admin.site.register(Teacher)
admin.site.register(Module)
admin.site.register(Takers)
admin.site.register(Page)
admin.site.register(ModuleVideo)
admin.site.register(PageVideo)
admin.site.register(Picture)
