from django.http import Http404
from rest_framework import viewsets

from api import models, serializers
from .mixins import AddPermission
from .utils import add_perms, add_project_perms


class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    lookup_field = 'name'


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    lookup_field = 'name'

    def get_queryset(self):
        account = self.kwargs['account']
        qs = models.Project.objects.filter(account__name=account)
        if self.request.user.has_perm('api.view_account', models.Account.objects.get(name=account)):
            return qs
        else:
            raise Http404("Account not found")

    def perform_create(self, serializer):
        account_name = self.kwargs['account']
        account = models.Account.objects.get(name=account_name)

        # Could have a validate_account method for serializer, but would then need to overwrite create()
        # which does more stuff, right now serializer class is clean, and we're doing stuff here anyway.
        if not self.request.user.has_perm('api.change_account', account):
            raise Http404("Account not found")
        obj = serializer.save(account=account)
        # Serializer is already saved, but calling this will do the post-processing permissions
        add_project_perms(self.request.user, obj)

    def perform_destroy(self, instance):
        agms = instance.account.groups.filter(name__contains=instance.name)
        for group in agms:
            group.grp.delete()
        instance.delete()


class EnvironmentViewSet(AddPermission, viewsets.ModelViewSet):
    serializer_class = serializers.EnvironmentSerializer
    lookup_field = 'name'

    def get_queryset(self):
        account_name = self.kwargs['account']
        project_name = self.kwargs['project']
        qs = models.Environment.objects.filter(project__account__name=account_name,
                                               project__name=project_name)
        print(qs)
        if self.request.user.has_perm('api.view_project',
                                      models.Project.objects.get(account__name=account_name,
                                                                 name=project_name)):
            return qs
        else:
            raise Http404("Account not found")

    def perform_create(self, serializer):
        account_name = self.kwargs['account']
        project_name = self.kwargs['project']
        project = models.Project.objects.get(account__name=account_name, name=project_name)

        # Could have a validate_account method for serializer, but would then need to overwrite create()
        # which does more stuff, right now serializer class is clean, and we're doing stuff here anyway.
        if not self.request.user.has_perm('api.change_project', project):
            raise Http404("Project not found")
        obj = serializer.save(project=project)
        # Serializer is already saved, but calling this will do the post-processing permissions
        add_perms(obj)


class PipelineViewSet(AddPermission, viewsets.ModelViewSet):
    queryset = models.Pipeline.objects.all()
    serializer_class = serializers.PipelineSerializer
    lookup_field = 'name'
