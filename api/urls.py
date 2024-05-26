# from rest_framework_extensions.routers import ExtendedDefaultRouter as DefaultRouter

from api import views

app_name = 'api'

# router = DefaultRouter()
# base_router = router.register('account', views.AccountViewSet, basename='account')
# project_router = base_router.register('project',
#                                       views.ProjectViewSet,
#                                       basename='project',
#                                       parents_query_lookups=['account'])
# project_router.register('environment',
#                         views.EnvironmentViewSet,
#                         basename='environment',
#                         parents_query_lookups=['project__account', 'project'])
# project_router.register('pipeline',
#                         views.PipelineViewSet,
#                         basename='pipeline',
#                         parents_query_lookups=['project__account', 'project'])
# project_router.register('repo',
#                         views.RepoViewSet,
#                         basename='repo',
#                         parents_query_lookups=['project__account', 'project'])

from django.urls import re_path

# urlpatterns = [re_path(r'^account/$', views.AccountViewSet.as_view(), name='account-list'),
#                re_path(r'^account/(?P<pk>[^/.]+)/$', views.AccountViewSet.as_view(), name='account-detail'),
#                re_path(r'^(?P<account>[^/.]+)/project/$', views.ProjectViewSet.as_view(), name='project-list'),
#                re_path(r'^(?P<account>[^/.]+)/(?P<pk>[^/.]+)/$', views.ProjectViewSet.as_view(), name='project-detail'),
#                re_path(r'^(?P<account>[^/.]+)/(?P<project>[^/.]+)/environment/$', views.EnvironmentViewSet.as_view(),
#                     name='environment-list'),
#                re_path(r'^(?P<account>[^/.]+)/(?P<project>[^/.]+)/(?P<pk>[^/.]+)/$', views.EnvironmentViewSet.as_view(),
#                     name='environment-detail'),
#                re_path(r'^(?P<account>[^/.]+)/(?P<project>[^/.]+)/pipeline/$', views.PipelineViewSet.as_view(),
#                     name='pipeline-list'),
#                re_path(r'^(?P<account>[^/.]+)/(?P<project>[^/.]+)/(?P<pk>[^/.]+)/$', views.PipelineViewSet.as_view(),
#                     name='pipeline-detail'),
#                ]
#
#
# urlpatterns = router.urls
# from pprint import pprint
# pprint(urlpatterns)



from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'account/$', views.AccountViewSet)
router.register(r'^(?P<account>[^/.]+)/projects', views.ProjectViewSet)
# router.register(r'^(?P<account>[^/.]+)/projects', views.ProjectViewSet)
urlpatterns = router.urls

