from collections import OrderedDict
import logging

from rest_framework import serializers

from api import mixins, models


logger = logging.getLogger()


# Execution App
class SlugFieldByProject(serializers.SlugRelatedField):
    def get_queryset(self):
        query_set = super().get_queryset()
        request = self.context.get('request')
        account = request.auth['account']
        project = request.auth['project']
        project = models.Project.objects.get(account__name=account, name=project)
        return query_set.filter(project=project)


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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('name',)


class EnvironmentSerializer(serializers.ModelSerializer):
    env_vars = EnvVarDictField(allow_null=True, default={})

    def create(self, validated_data):
        env_vars = validated_data.pop('env_vars', [])
        environment = models.Environment.objects.create(**validated_data)
        for env_var in env_vars:
            models.EnvVar.objects.get_or_create(environment=environment, **env_var)
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
                models.EnvVar.objects.get_or_create(environment=instance, **env_var)
        return instance

    class Meta:
        model = models.Environment
        fields = ('name', 'env_vars')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('name', 'command')


class StageSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(required=False, many=True)
    environments = SlugFieldByProject(required=False,
                                      queryset=models.Environment.objects.all(),
                                      many=True,
                                      slug_field="name")

    def create(self, validated_data):
        tasks = validated_data.pop('tasks', [])
        environments = validated_data.pop('environments', [])
        stage = models.Stage.objects.create(**validated_data)
        stage.environments.add(*environments)
        for task in tasks:
            models.Task.objects.get_or_create(stage=stage, **task)
        return stage

    def update(self, instance, validated_data):
        tasks = validated_data.pop('tasks', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if tasks is not None:
            # Clear existing env_vars
            instance.tasks.all().delete()
            # Add new environments
            for task in tasks:
                models.Task.objects.get_or_create(stage=instance, **task)
        return instance

    class Meta:
        model = models.Stage
        depth = 1
        fields = ('name', 'tasks', "environments")


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageSerializer(required=False, many=True)
    environments = SlugFieldByProject(required=False,
                                      queryset=models.Environment.objects.all(),
                                      many=True,
                                      slug_field="name")

    def validate_environments(self, value):
        if len(value) > 1:
            raise serializers.ValidationError("Pipelines can only be assigned to one environment")
        else:
            return value

    def create(self, validated_data):
        environments = validated_data.pop('environments', [])
        stages = validated_data.pop('stages', [])
        pipeline = models.Pipeline.objects.create(**validated_data)
        for stage in stages:
            print(stage)
            models.Stage.objects.get_or_create(name=stage, project=pipeline.project)
            pipeline.stages.add(stage)
        for env in environments:
            print(env)
            models.Environment.objects.get_or_create(name=env, project=pipeline.project)
            pipeline.environments.add(env)
        return pipeline

    def update(self, instance, validated_data):
        environments = validated_data.pop('environments', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if environments is not None:
            # Clear existing env_vars
            instance.environments.all().delete()
            # Add new environments
            for env in environments:
                models.Environment.objects.get_or_create(name=env, project=instance.project)
        return instance

    class Meta:
        model = models.Pipeline
        depth = 2
        fields = ('name', 'stages', 'environments')


class ProjectSerializer(serializers.ModelSerializer):
    environments = SlugFieldByProject(required=False,
                                      queryset=models.Environment.objects.all(),
                                      many=True,
                                      slug_field="name")
    pipelines = SlugFieldByProject(required=False,
                                   queryset=models.Pipeline.objects.all(),
                                   many=True,
                                   slug_field="name")

    class Meta:
        model = models.Project
        fields = ('name', 'environments', 'pipelines')


# Trigger app
class ScmPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScmPoll
        fields = ('branch', 'shallow_clone', 'ref', 'user')


class ScmWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScmWebhook
        fields = ('webhook_secret',)


class GitSerializer(mixins.NestedCreateMixin, serializers.ModelSerializer):
    map = {
        'poll': ScmPollSerializer,
        'webhook': ScmWebhookSerializer
    }
    model = models.Git
    field = 'git'

    poll = ScmPollSerializer(required=False)
    webhook = ScmWebhookSerializer(required=False)

    class Meta:
        model = models.Git
        fields = ('name', 'url', 'poll', 'webhook')

    def update(self, instance, validated_data):
        poll = validated_data.pop('poll', [])
        webhook = validated_data.pop('webhook', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if poll is not None:
            models.ScmPoll.objects.update_or_create(poll, git=instance)
        return instance

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key]])


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScmWebhook
        fields = ('webhook_secret',)
