from django.http import Http404
from rest_framework import viewsets, serializers

import api.serializers
from api import models, utils


class GetQuerySet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = dict()
        for k, v in self.request.query_params.items():
            if v in ['True', 'true', 1]:
                query_params[k] = True
            elif v in ['False', 'false', 0]:
                query_params[k] = False
            else:
                query_params[k] = v
        project_name = self.request.auth['project']
        account_name = self.request.auth['account']
        qs = queryset.filter(project__account__name=account_name,
                             project__name=project_name,
                             **query_params)
        return qs


class NestedMixin(serializers.ModelSerializer):
    def get_initial(self):
        initial_data = super().get_initial()
        if hasattr(self.Meta.model, 'project'):
            acct, project = utils.get_project_account_from_token(self.context.get('request'))
            initial_data['project'] = project
        return initial_data

    # def validate(self, data):
    #     super().validate(attrs=data)
    #     if hasattr(self.Meta.model, 'project'):
    #         acct, project = utils.get_project_account_from_token(self.context.get('request'))
    #         data['project'] = project
    #     return data

    # def create(self, validated_data):
    #     # Pull out nested data
    #     nested_data = dict()
    #     for field, data in list(validated_data.items()):
    #         if field in self.map:
    #             nested_data[self.map[field]] = validated_data.pop(field)
    #
    #     # Create the main root_model object
    #     root_model = self.Meta.model.objects.create(**validated_data)
    #     utils.add_perms(root_model)
    #
    #     # Use the sub-serializer to handle the nested data
    #     # If data is a list we call the serializer class with many=True
    #     for serializer_class, data in nested_data.items():
    #         if type(data) == list and len(data) > 0:
    #             if isinstance(data[0], models.models.Model):
    #                 # d =
    #                 serializer = serializer_class(data=data, many=True)
    #                 manager_field = data[0]._meta.verbose_name_plural
    #                 manager = getattr(root_model, manager_field)
    #                 root_model.environments.add(*data)
    #                 # manager.add(*data)
    #                 # if data[0]._meta.verbose_name_plural == 'environments':
    #                 #     root_model.environments.add(*data)
    #                 #     return root_model
    #             else:
    #                 serializer = serializer_class(data=data, many=True)
    #         else:
    #             serializer = serializer_class(data=data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save(**{self.field: root_model})
    #     return root_model

    # def update(self, instance, validated_data):
    #     nested_data = dict()
    #     for field, data in list(validated_data.items()):
    #         if field in self.map:
    #             nested_data[self.map[field]] = validated_data.pop(field)
    #
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.save()
    #     if tasks is not None:
    #         # Clear existing env_vars
    #         instance.tasks.all().delete()
    #         # Add new environments
    #         for task in tasks:
    #             models.Task.objects.get_or_create(stage=instance, **task)
    #     return instance
