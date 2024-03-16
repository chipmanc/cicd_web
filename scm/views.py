from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets

from scm import models, serializers
from scm.drivers import SCMRegistry


class GitRepoViewSet(viewsets.ModelViewSet):
    queryset = models.Repo.objects.all()
    serializer_class = serializers.GitRepoSerializer


@csrf_exempt
def receive_webhook(request):
<<<<<<< Updated upstream
    driver = SCMRegistry()
    pipelines = driver.get_pipelines(request)
    driver.trigger_pipeline(pipelines, 'chri')
=======
    driver = SCMManager()
    #pipelines = driver.get_pipelines(request)
    #driver.trigger_pipeline(pipelines, 'chri')
    # app.send_task('scm.tasks.task', (1,), {'task': 'ls', 'shell': '/bin/bash'})
    # app.send_task('scm.tasks.task', ('apply',), {'task': 'terraform', 'shell': '/bin/bash'})
    # app.send_task('scm.tasks.task', ('inventory_file',), {'task': 'ansible-playbook', 'shell': '/bin/bash'})
    app.send_task('worker.tasks.run', (), {'repo': 'https://github.com/chipmanc/AdminScripts.git', 'command': 'ls', 'shell': '/bin/bash'})
>>>>>>> Stashed changes
    return HttpResponse('')
