from django.http import Http404
from rest_framework import viewsets

from api import models, utils


class AddPermission(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        account_name = self.request.auth['account']
        project_name = self.request.auth['project']
        project = models.Project.objects.get(name=project_name, account__name=account_name)
        if not self.request.user.has_perm('api.change_project', project):
            raise Http404("Account not found")
        obj = serializer.save(project=project)
        # Serializer is already saved, but calling this will do the post-processing permissions
        utils.add_perms(obj)


class GetQuerySet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        project_name = self.request.auth['project']
        account_name = self.request.auth['account']

        qs = queryset.filter(project__account__name=account_name,
                             project__name=project_name)
        return qs


class NestedCreateMixin:
    map = {}
    model = None
    field = None

    def create(self, validated_data):
        # Map root_model to serializer
        for key, value in list(validated_data.items()):
            if key in self.map:
                sub_serializer_class = self.map[key]
                data = validated_data.pop(key)

        # Create the main root_model object using the model
        root_model = self.model.objects.create(**validated_data)

        # Use the sub-serializer to handle the nested data
        sub_serializer = sub_serializer_class(data=data)
        sub_serializer.is_valid(raise_exception=True)
        sub_serializer.save(**{self.field: root_model})

        return root_model
