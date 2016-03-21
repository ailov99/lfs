from django.conf.urls import patterns, url
from lfs_admin import views
#from django.views.generic import TemplateView

urlpatterns = patterns('',
        
        url(r'^$', views.index, name='admin_index'),
        url(r'^dashboard/$', views.admin_dashboard, name="dashboard"),
        url(r'^guide/$', views.admin_guide, name="guide"),
        url(r'^change_colour_scheme/$', views.change_colour_scheme, name="change_colour_scheme"),
        url(r'^stats/$', views.admin_stats, name="stats"),
        url(r'^admin/$', views.admin, name="admin"),
        url(r'^add_module/$', views.add_module, name="add_module"),
        url(r'^edit_module/(?P<moduleid>[\w\-]+)/$', views.edit_module, name="edit_module"),
        url(r'^add_page/(?P<moduleid>[\w\-]+)/$', views.add_page, name="add_page"),
        url(r'^edit_page/(?P<pageid>[\w\-]+)/$', views.edit_page, name="edit_page"),
        url(r'^delete_page/(?P<pageid>[\w\-]+)/$', views.delete_page, name="delete_page"),
        url(r'^delete_module/(?P<moduleid>[\w\-]+)/$', views.delete_module, name="delete_module"),
        url(r'^user_list/$', views.user_list, name="user_list"),
        url(r'^promote_user/(?P<userid>[\w\-]+)$', views.promote_user, name="promote_user"),
        #url(r'^admin_guide/$', TemplateView.as_view(template_name="admin_guide.html")),
       )
