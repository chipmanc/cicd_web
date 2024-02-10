from rest_framework_extensions.routers import ExtendedDefaultRouter as DefaultRouter

from api import views

router = DefaultRouter()
base_router = router.register('account', views.AccountViewSet, basename='account')
project_router = base_router.register('project',
                                      views.ProjectViewSet,
                                      basename='project',
                                      parents_query_lookups=['account'])
project_router.register('environment',
                        views.EnvironmentViewSet,
                        basename='environment',
                        parents_query_lookups=['project__account', 'project'])
project_router.register('pipeline',
                        views.PipelineViewSet,
                        basename='pipeline',
                        parents_query_lookups=['project__account', 'project'])


app_name = 'api'
urlpatterns = router.urls
