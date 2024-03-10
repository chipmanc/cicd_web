from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets

from cicd import app
from scm import models, serializers
from scm.drivers import SCMManager


class RepoViewSet(viewsets.ModelViewSet):
    queryset = models.Repo.objects.all()
    serializer_class = serializers.GitRepoSerializer


@csrf_exempt
def receive_webhook(request):
    driver = SCMManager()
    pipelines = driver.get_pipelines(request)
    driver.trigger_pipeline(pipelines, 'chri')
    app.send_task('worker.tasks.run', (), {'command': None, 'shell': '/bin/bash'})
    return HttpResponse('')







@csrf_exempt
def receive_webhook(request):
    driver = SCMManager()
    app.send_task('scm.tasks.task', (1,), {'task': 'ls', 'shell': '/bin/bash'})
    app.send_task('scm.tasks.task', ('apply',), {'task': 'terraform', 'shell': '/bin/bash'})
    app.send_task('scm.tasks.task', ('inventory_file',), {'task': 'ansible-playbook', 'shell': '/bin/bash'})
    #pipelines = driver.get_pipelines(request)
    #driver.trigger_pipeline(pipelines, 'chri')
    return HttpResponse('')
