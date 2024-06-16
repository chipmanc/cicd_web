import logging

from rest_framework import serializers

from api import models


logger = logging.getLogger()


class SlugFieldByProject(serializers.SlugRelatedField):
    def get_queryset(self):
        query_set = super().get_queryset()
        request = self.context.get('request')
        account = request.parser_context['kwargs']['account']
        project = request.parser_context['kwargs']['project']
        project = models.Project.objects.get(account__name=account, name=project)
        return query_set.filter(project=project)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('name',)


class EnvVarDictField(serializers.Field):
    def to_representation(self, value):
        # Convert the queryset of EnvVar instances to a dictionary
        env_vars = {}
        for env_var in value.all():
            env_vars[env_var.key] = env_var.value
        return env_vars

    def to_internal_value(self, data):
        # Convert the dictionary back to a queryset of EnvVar instances
        if not isinstance(data, dict):
            raise serializers.ValidationError('This field should be a dictionary.')

        env_vars = []
        for key, value in data.items():
            env_vars.append({'key': key, 'value': value})
        return env_vars


class EnvironmentSerializer(serializers.ModelSerializer):
    env_vars = EnvVarDictField(allow_null=True, default={})
    project = models.Project

    def create(self, validated_data):
        env_vars = validated_data.pop('env_vars', [])
        environment = models.Environment.objects.create(**validated_data)
        for env_var in env_vars:
            models.EnvVar.objects.create(environment=environment, **env_var)
        return environment

    def update(self, instance, validated_data):
        env_vars = validated_data.pop('env_vars', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if env_vars is not None:
            # Clear existing env_vars
            instance.env_vars.all().delete()
            # Add new env_vars
            for env_var in env_vars:
                models.EnvVar.objects.create(environment=instance, **env_var)
        return instance

    class Meta:
        model = models.Environment
        fields = ('name', 'env_vars')


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Job
        fields = ('name',)


class StageSerializer(serializers.ModelSerializer):
    jobs = JobSerializer(required=False, many=True)

    class Meta:
        model = models.Stage
        depth = 1
        fields = ('name', 'jobs')


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageSerializer(required=False, many=True)
    environments = SlugFieldByProject(queryset=models.Environment.objects.all(), many=True, slug_field="name")

    def create(self, validated_data):
        envs = validated_data.pop('environments', [])
        logger.error(envs)
        pipeline = models.Pipeline.objects.create(**validated_data)
        for env in envs:
            models.Environment.objects.create(name=env, project=pipeline.project)
        return pipeline

    def update(self, instance, validated_data):
        envs = validated_data.pop('environments', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if envs is not None:
            # Clear existing env_vars
            instance.environments.all().delete()
            # Add new env_vars
            for env in envs:
                models.Environment.objects.create(name=env, project=instance.project)
        return instance

    class Meta:
        model = models.Pipeline
        depth = 2
        fields = ('name', 'stages', 'environments')


class ProjectSerializer(serializers.ModelSerializer):
    account = models.Account
    environments = SlugFieldByProject(queryset=models.Environment.objects.all(), many=True, slug_field="name")
    pipelines = SlugFieldByProject(queryset=models.Pipeline.objects.all(), many=True, slug_field="name")

    class Meta:
        model = models.Project
        fields = ('name', 'environments', 'pipelines')
