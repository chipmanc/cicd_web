from django.urls import re_path
from rest_framework_extensions.routers import ExtendedDefaultRouter as DefaultRouter

from api import views

app_name = 'api'

from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'account', views.AccountViewSet)
router.register(r'(?P<account>[^/.]+)/projects', views.ProjectViewSet)
router.register(r'(?P<account>[^/.]+)/(?P<project>[^/.]+)/environments', views.EnvironmentViewSet)
router.register(r'(?P<account>[^/.]+)/(?P<project>[^/.]+)/pipelines', views.PipelineViewSet)

urlpatterns = router.urls

