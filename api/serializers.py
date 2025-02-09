from collections import OrderedDict
import logging

from rest_framework import serializers

from api import mixins, models, utils

logger = logging.getLogger()


# Execution App
class SlugFieldByProject(serializers.SlugRelatedField):
    def get_queryset(self):
        query_set = super().get_queryset()
        acct, project = utils.get_project_account_from_token(self.context.get('request'))
        # project = models.Project.objects.filter(account='test1', name='default').first()
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


class EnvVarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnvVar
        fields = ['key', 'value']


class EnvironmentSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    map = {
        'env_vars': 'EnvVarSerializer'
    }
    field = 'environment'

    env_vars = EnvVarDictField(allow_null=True, default={})

    class Meta:
        model = models.Environment
        fields = ('name', 'env_vars')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ('name', 'command')


class StageSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    map = {
        "tasks": 'TaskSerializer'
    }
    field = 'stage'

    tasks = TaskSerializer(many=True)

    class Meta:
        model = models.Stage
        depth = 1
        fields = ('name', 'tasks')


class StageAttachmentSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    map = {
        'environments': 'EnvironmentSerializer',
        'resources': 'GitSerializer'
    }
    field = 'stages'
    exclude = ['pipeline', 'name']

    name = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name")
    on_success = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name", many=True, required=False)
    on_fail = SlugFieldByProject(queryset=models.Stage.objects.all(), slug_field="name", many=True, required=False)
    resources = SlugFieldByProject(queryset=models.Git.objects.all(), slug_field="name", many=True, required=False)
    environments = SlugFieldByProject(required=False,
                                      queryset=models.Environment.objects.all(),
                                      many=True,
                                      slug_field="name")

    class Meta:
        model = models.StageAttachment
        fields = ['name', 'resources', 'environments', 'on_success', 'on_fail']


class PipelineSerializer(mixins.NestedMixin, serializers.ModelSerializer):
    map = {
        'stages': 'StageAttachmentSerializer',
    }
    field = 'pipeline'

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


class ReadOnlyStageAttachmentSerializer(serializers.ModelSerializer):
    name = StageSerializer()
    resources = SlugFieldByProject(queryset=models.Git.objects.all(), slug_field="name", many=True)
    environments = EnvironmentSerializer(many=True)

    class Meta:
        model = models.StageAttachment
        fields = ['name', 'environments', 'resources']
        depth = 3


class ReadOnlyPipelineSerializer(serializers.ModelSerializer):
    stages = ReadOnlyStageAttachmentSerializer(many=True)
    environment = EnvironmentSerializer()

    class Meta:
        model = models.Pipeline
        fields = ['name', 'environment', 'stages']
        depth = 3


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
        'poll': 'ScmPollSerializer',
        'webhook': 'ScmWebhookSerializer'
    }
    field = 'git'

    poll = ScmPollSerializer(required=False)
    webhook = ScmWebhookSerializer(required=False)
    stages = serializers.StringRelatedField(required=False, read_only=True, many=True)

    class Meta:
        model = models.Git
        fields = ('name', 'url', 'poll', 'webhook', 'stages')

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key]])


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ScmWebhook
        fields = ('webhook_secret',)
