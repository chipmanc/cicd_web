from django.http import Http404
from rest_framework import viewsets

from api import models, utils


class AddPermission(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        account_name = self.kwargs['account']
        project_name = self.kwargs['project']
        project = models.Project.objects.get(name=project_name, account__name=account_name)
        if not self.request.user.has_perm('api.change_project', project):
            raise Http404("Account not found")
        obj = serializer.save(project=project)
        # Serializer is already saved, but calling this will do the post-processing permissions
        utils.add_perms(obj)


class GetQuerySet(viewsets.ModelViewSet):
    def get_queryset(self):
        account_name = self.kwargs['account']
        project_name = self.kwargs['project']
        qs = models.Environment.objects.filter(project__account__name=account_name,
                                               project__name=project_name)
        return qs
        # if self.request.user.has_perm('api.view_project',
        #                               models.Project.objects.get(account__name=account_name,
        #                                                          name=project_name)):
        #     return qs
        # else:
        #     raise Http404("Account not found")
