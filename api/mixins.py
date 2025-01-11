from django.db.models.fields.related_descriptors import *
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
    map = {}
    field = ''
    exclude = []
    Meta = None

    def map_attr_to_type(self, data):
        relations = {"ReverseManyToMany": [],
                     "ForwardManyToMany": [],
                     "ManyToMany": []}
        for attribute, value in list(data.items()):
            if attribute in self.exclude:
                continue
            attr_type = type(getattr(self.Meta.model, attribute))
            if attr_type == ReverseManyToOneDescriptor:
                relations['ReverseManyToMany'].append((attribute, data.pop(attribute)))
            elif attr_type == ForwardManyToOneDescriptor:
                relations['ForwardManyToMany'].append((attribute, data.pop(attribute)))
            elif attr_type == ManyToManyDescriptor:
                relations['ManyToMany'].append((attribute, data.pop(attribute)))
        return relations

    def create(self, validated_data):
        project = validated_data.pop('project', None)
        relations = self.map_attr_to_type(validated_data)

        if hasattr(self.Meta.model, 'project'):
            instance = self.Meta.model.objects.create(**validated_data, project=project)
            utils.add_perms(instance)
        else:
            instance = self.Meta.model.objects.create(**validated_data)

        for nest in relations['ReverseManyToMany']:
            sub_serializer = getattr(api.serializers, self.map[nest[0]])
            if isinstance(nest[1], list):
                nested_field = sub_serializer(data=nest[1], many=True)
            else:
                nested_field = sub_serializer(data=nest[1])
            nested_field.is_valid(raise_exception=True)
            nested_field.save(**{self.field: instance})
        for nest in relations['ForwardManyToMany']:
            nested_model_type = getattr(nest[1], '__class__')
            nested_field, _ = nested_model_type.objects.get_or_create(name=nest[1],
                                                                      project=project)
            setattr(instance, nest[0], nest[1])
            instance.save()
        for nest in relations['ManyToMany']:
            project = getattr(instance, self.exclude[0]).project
            field, instances = nest
            for i in instances:
                nested_model_type = getattr(i, '__class__')
                nested_field, _ = nested_model_type.objects.get_or_create(name=i,
                                                                          project=project)
                nested_manager = getattr(instance, field)
                nested_manager.add(nested_field)

        return instance

    def update(self, instance, validated_data):
        project = validated_data.pop('project', None)
        relations = self.map_attr_to_type(validated_data)
        instance.save()

        for nest in relations['ReverseManyToMany']:
            sub_serializer = getattr(api.serializers, self.map[nest[0]])
            if self.context['view'].action == 'update':
                manager = getattr(instance, nest[0])
                manager.get_queryset().delete()
                if isinstance(nest[1], list):
                    nested_field = sub_serializer(data=nest[1], many=True)
                else:
                    nested_field = sub_serializer(data=nest[1])
                nested_field.is_valid(raise_exception=True)
                nested_field.save(**{self.field: instance})
            elif self.context['view'].action == 'partial_update':
                nested_cls = getattr(instance, nest[0]).model
                for nested_data in nest[1]:
                    nest_data = nested_data.copy()
                    nest_data.update({self.field: instance})
                    nest_data = {key: nest_data[key] for key in nest_data.keys() & {'name', 'key', self.field}}
                    sub_instance = nested_cls.objects.get(**nest_data)
                    nested_field = sub_serializer(data=nested_data)
                    nested_field.is_valid(raise_exception=True)
                    nested_field.update(sub_instance, nested_data)
        for nest in relations['ForwardManyToMany']:
            nested_cls = getattr(nest[1], '__class__')
            nested_field, _ = nested_cls.objects.get(name=nest[1], project=project)
            setattr(instance, nest[0], nest[1])
        for nest in relations['ManyToMany']:
            project = getattr(instance, self.exclude[0]).project
            field, instances = nest
            nested_manager = getattr(instance, field)
            for i in instances:
                nested_manager.add(i)
            instance.save()

        return instance

    def validate(self, data):
        super().validate(attrs=data)
        if hasattr(self.Meta.model, 'project'):
            acct, project = utils.get_project_account_from_token(self.context.get('request'))
            data['project'] = project
        return data
