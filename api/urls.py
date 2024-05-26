from rest_framework import routers

from api import views


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'account', views.AccountViewSet)
router.register(r'(?P<account>[^/.]+)/projects', views.ProjectViewSet, basename='project')
router.register(r'(?P<account>[^/.]+)/(?P<project>[^/.]+)/environments', views.EnvironmentViewSet)
router.register(r'(?P<account>[^/.]+)/(?P<project>[^/.]+)/pipelines', views.PipelineViewSet)

urlpatterns = router.urls
