from django.conf.urls import patterns, url

from .views import QuizListView, ModulesListView,\
    QuizUserProgressView, QuizMarkingList,\
    QuizMarkingDetail


urlpatterns = patterns('',

                       url(regex=r'^$',
                           view=QuizListView.as_view(),
                           name='quiz_index'),

                       url(regex=r'^module/$',
                           view=ModulesListView.as_view(),
                           name='quiz_category_list_all'),


                       url(regex=r'^progress/$',
                           view=QuizUserProgressView.as_view(),
                           name='quiz_progress'),

                       url(regex=r'^marking/$',
                           view=QuizMarkingList.as_view(),
                           name='quiz_marking'),

                       url(regex=r'^marking/(?P<pk>[\d.]+)/$',
                           view=QuizMarkingDetail.as_view(),
                           name='quiz_marking_detail'),
)
