from django.conf.urls import patterns, url, include
from lfs import views
from lfs_quiz.views import QuizDetailView, QuizTake
from django.views.generic import TemplateView

# from django.contrib.auth.views import *

urlpatterns = patterns('',
                       # Basic user navigation
                       url(r'^$', views.user_dashboard, name='index'),
                       url(r'^register/$', views.user_register, name="register"),
                       url(r'^login/$', views.user_login, name="login"),
                       url(r'^logout/$', views.user_logout, name="logout"),
                       url(r'^dashboard/$', views.user_dashboard, name="dashboard"),
                       url(r'^profile/(?P<userid>[\w\-]+)/$', views.profile, name="profile"),
                       url(r'^profile/(?P<userid>[\w\-]+)/edit/$', views.edit_profile, name="edit_profile"),
                       url(r'^forum/$', views.forum, name="forum"),
                       url(r'^contact_admin/(?P<userid>[\w\-]+)$', views.user_contact_admin, name="contact_admin"),
                       url(r'^leaderboard/$', views.leaderboard, name="leaderboard"),
                       url(r'^admin_guide/$', views.admin_guide, name="admin_guide"),
                       url(r'^subscription/(?P<userid>[\w\-]+)$', views.user_subscription, name="subscription"),
                       url(r'^change_password/$', views.change_password, name="change_password"),
                       url(r'^update_progress/(?P<moduleid>[\w\-]+)/(?P<pagenum>[\w\-]+)$', views.update_progress,
                           name="update_progress"),

                       # Modules functionality
                       url(r'^modules/$', views.modules, name="modules"),
                       url(r'^download/(?P<contentid>[\w\-]+)$', views.download_content, name="download_content"),
                       url(r'^module/(?P<moduleid>[\w\-]+)/$', views.module, name="module"),
                       url(r'^module/(?P<moduleid>[\w\-]+)/quiz/$', view=QuizDetailView.as_view(),
                           name='quiz_start_page'),
                       url(r'^module/(?P<moduleid>[\w\-]+)/quiz/take$', view=QuizTake.as_view(), name='quiz_question'),
                       url(r'^pick_module/(?P<moduleid>[\w\-]+)/$', views.pick_module, name="pick_module"),
                       url(r'^drop_module/(?P<moduleid>[\w\-]+)/$', views.drop_module, name="drop_module"),

                       # Trial functionality
                       url(r'^trial/$', views.trial_dashboard, name="trial_dashboard"),
                       url(r'^trial/module/(?P<moduleid>[\w\-]+)/$', views.trial_module, name="trial_module"),

                       # Messaging functionality
                       url(r'^messages/(?P<userid>[\w\-]+)$', views.user_messages, name="messages"),
                       url(r'^messages/(?P<messageid>[\w\-]+)$', views.message, name="message"),
                       url(r'^messages/(?P<messageid>[\w\-]+)/send/$', views.message_send, name="send_message"),

                       )
