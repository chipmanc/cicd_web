from django.http import Http404
from rest_framework import viewsets

from api import models, utils


class AddPermission(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        project_name = self.kwargs['project']
        project = models.Project.objects.get(name=project_name)
        if not self.request.user.has_perm('api.change_project', project):
            raise Http404("Account not found")
        obj = serializer.save(project=project)
        # Serializer is already saved, but calling this will do the post-processing permissions
        utils.add_perms(obj)
