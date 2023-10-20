from django.http import Http404
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from api import models, serializers
from .mixins import AddPermission
from .utils import add_project_perms


class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer


class ProjectViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()
    basename = 'project'

    def perform_create(self, serializer):
        account_pk = self.kwargs['parent_lookup_account']
        account = models.Account.objects.get(pk=account_pk)
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


class EnvironmentViewSet(AddPermission, NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Environment.objects.all()
    serializer_class = serializers.EnvironmentSerializer


class PipelineViewSet(AddPermission, NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Pipeline.objects.all()
    serializer_class = serializers.PipelineSerializer
