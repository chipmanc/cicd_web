from django.http import Http404
from rest_framework import permissions
from rest_framework import viewsets

from api import models, serializers
from .mixins import AddPermission, GetQuerySet
from .utils import add_project_perms


class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    lookup_field = 'name'


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    lookup_field = 'name'

    def get_queryset(self):
        account = self.request.auth['account']
        qs = models.Project.objects.filter(account__name=account)
        if self.request.user.has_perm('api.view_account', models.Account.objects.get(name=account)):
            return qs
        else:
            raise Http404("Account not found")

    def perform_create(self, serializer):
        account_name = self.request.auth['account']
        account = models.Account.objects.get(name=account_name)
        # if not self.request.user.has_perm('api.change_account', account):
        #     raise Http404("Account not found")
        obj = serializer.save(account=account)
        # Serializer is already saved, but calling this will do the post-processing permissions
        add_project_perms(self.request.user, obj)

    def perform_destroy(self, instance):
        account_name = self.request.auth['account']
        groups = models.Group.objects.filter(name__startswith=f'{account_name}-{instance.name}')
        for group in groups:
            group.delete()
        instance.delete()


class EnvironmentViewSet(AddPermission, GetQuerySet, viewsets.ModelViewSet):
    queryset = models.Environment.objects.all()
    serializer_class = serializers.EnvironmentSerializer
    lookup_field = 'name'


class PipelineViewSet(AddPermission, GetQuerySet, viewsets.ModelViewSet):
    queryset = models.Pipeline.objects.all()
    serializer_class = serializers.PipelineSerializer
    permission_classes = (permissions.DjangoObjectPermissions,)
    lookup_field = 'name'


class StageViewSet(AddPermission, GetQuerySet, viewsets.ModelViewSet):
    queryset = models.Stage.objects.all()
    serializer_class = serializers.StageSerializer
    permission_classes = (permissions.DjangoObjectPermissions,)
    lookup_field = 'name'
