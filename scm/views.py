from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import viewsets

from scm import models, serializers
from scm.drivers import scm_registry


class GitRepoViewSet(viewsets.ModelViewSet):
    queryset = models.GitRepo.objects.all()
    serializer_class = serializers.GitRepoSerializer


@csrf_exempt
def receive(request):
    body = request.body
    headers = request.headers
    return HttpResponse('')
