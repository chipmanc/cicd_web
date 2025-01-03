from rest_framework import routers

from api import views


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'account', views.AccountViewSet, basename='account')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'environments', views.EnvironmentViewSet, basename='environment')
router.register(r'pipelines', views.PipelineViewSet, basename='pipeline')
router.register(r'stages', views.StageViewSet, basename='stage')
router.register(r'git', views.GitViewSet, basename='git')
# router.register(r'agents', views.TriggerViewSet, basename='agent')

urlpatterns = router.urls

# TEST
from django.urls import path
urlpatterns.append(path("choose/", views.index, name="index"))
urlpatterns.append(path("<str:room_name>/", views.room, name="room"))
