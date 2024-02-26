from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets

from scm import models, serializers
from scm.drivers import SCMManager


class GitRepoViewSet(viewsets.ModelViewSet):
    queryset = models.Repo.objects.all()
    serializer_class = serializers.GitRepoSerializer


@csrf_exempt
def receive_webhook(request):
    driver = SCMManager()
    pipelines = driver.get_pipelines(request)
    driver.trigger_pipeline(pipelines, 'chri')
    return HttpResponse('')
