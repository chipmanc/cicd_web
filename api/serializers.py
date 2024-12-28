from collections import OrderedDict
import logging

from rest_framework import serializers

from api import mixins, models, utils

logger = logging.getLogger()


# Execution App
class SlugFieldByProject(serializers.SlugRelatedField):
    def get_queryset(self):
        query_set = super().get_queryset()
        # acct, project = utils.get_project_account_from_token(self.context.get('request'))
        project = models.Project.objects.filter(account='test1', name='default').first()
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

    class Meta:
        model = models.EnvVar
        fields = ['key', 'value']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ('name',)


class EnvironmentSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    env_vars = EnvVarDictField(allow_null=True, default={})

    def create(self, validated_data):
        env_vars = validated_data.pop('env_vars', None)
        root_model = models.Environment.objects.create(**validated_data)
        utils.add_perms(root_model)
        if env_vars:
            envvar_instances = []
            for env_var in env_vars:
                env_var.setdefault('environment', root_model)
                envvar_instances.append(models.EnvVar(**env_var))
            models.EnvVar.objects.bulk_create(envvar_instances)
        return root_model

    def update(self, instance, validated_data):
        env_vars = validated_data.pop('env_vars', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if env_vars:
            envvar_instances = []
            instance.env_vars.all().delete()
            for env_var in env_vars:
                env_var.setdefault('environment', instance)
                envvar_instances.append(models.EnvVar(**env_var))
            models.EnvVar.objects.bulk_create(envvar_instances)
        return instance

    class Meta:
        model = models.Environment
        fields = ('name', 'env_vars')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('name', 'command')


class StageSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    tasks = TaskSerializer(many=True)

    def create(self, validated_data):
        tasks = validated_data.pop('tasks', None)
        stage = models.Stage.objects.create(**validated_data)
        utils.add_perms(stage)
        if tasks:
            task_instances = []
            for task in tasks:
                task.setdefault('stage', stage)
                task_instances.append(models.Task(**task))
            models.Task.objects.bulk_create(task_instances)
        return stage

    def update(self, instance, validated_data):
        tasks = validated_data.pop('tasks', None)
        environments = validated_data.pop('environments', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if tasks:
            instance.tasks.all().delete()
            serializer = TaskSerializer(data=tasks, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(stage=instance)
        return instance

    class Meta:
        model = models.Stage
        depth = 1
        fields = ('name', 'tasks', "environments")


class StageAttachmentSerializer(serializers.ModelSerializer):
    name = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name")
    on_success = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name", many=True, required=False)
    on_fail = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name", many=True, required=False)
    resources = SlugFieldByProject(queryset=models.Git.objects.all(), slug_field="name", many=True)
    environments = SlugFieldByProject(required=False,
                                      queryset=models.Environment.objects.all(),
                                      many=True,
                                      slug_field="name")

    class Meta:
        model = models.StageAttachment
        fields = ['name', 'resources', 'environments', 'on_success', 'on_fail']

    def create(self, validated_data):
        environments = validated_data.pop('environments', None)
        resources = validated_data.pop('resources', None)
        stage_attachment = models.StageAttachment.objects.create(**validated_data)
        stage_attachment.environments.set(environments)
        stage_attachment.resources.set(resources)
        return stage_attachment

    def update(self, instance, validated_data):
        environments = validated_data.pop('environments', None)
        if environments:
            instance.environments.clear()
            instance.environments.add(*environments)
        pass


class PipelineSerializer(serializers.ModelSerializer):
    stages = StageAttachmentSerializer(many=True)
    environment = SlugFieldByProject(required=False,
                                     queryset=models.Environment.objects.all(),
                                     slug_field="name")

    class Meta:
        model = models.Pipeline
        depth = 2
        fields = ('name', 'stages', 'environment')

    @staticmethod
    def validate_environments(self, value):
        if len(value) > 1:
            raise serializers.ValidationError("Pipelines can only be assigned to one environment")
        else:
            return value

    def create(self, validated_data):
        environments = validated_data.pop('environments', None)
        stages = validated_data.pop('stages', None)
        pipeline = models.Pipeline.objects.create(**validated_data)
        utils.add_perms(pipeline)
        for stage in stages:
            stg = StageAttachmentSerializer(data=stage)
            stg.is_valid()
            stg = stg.save(pipeline=pipeline)
            pipeline.stages.add(stg)
        # for env in environments:
        #     models.Environment.objects.get_or_create(name=env, project=pipeline.project)
        #     pipeline.environments.add(env)
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


class GitSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    map = {
        'poll': ScmPollSerializer,
        'webhook': ScmWebhookSerializer
    }
    field = 'git'

    poll = ScmPollSerializer(required=False)
    webhook = ScmWebhookSerializer(required=False)
    stages = serializers.StringRelatedField(required=False, read_only=True, many=True)

    class Meta:
        model = models.Git
        fields = ('name', 'url', 'poll', 'webhook', 'stages')

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
