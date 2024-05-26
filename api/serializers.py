from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from api import models


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


class EnvVarSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnvVar
        fields = ('name', 'value')


class EnvironmentSerializer(WritableNestedModelSerializer):
    env_vars = EnvVarSerializer(required=False, many=True)

    class Meta:
        model = models.Environment
        fields = ('name', 'env_vars')


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Job
        fields = ('name',)


class StageSerializer(WritableNestedModelSerializer):
    jobs = JobSerializer(required=False, many=True)

    class Meta:
        model = models.Stage
        depth = 1
        fields = ('name', 'jobs')


class PipelineSerializer(WritableNestedModelSerializer):
    stages = StageSerializer(required=False, many=True)
    environments = SlugFieldByProject(queryset=models.Environment.objects.all(), many=True, slug_field="name")

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
