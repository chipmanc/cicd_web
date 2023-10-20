from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer

from api import models


class PrimaryKeyRelatedFieldByProject(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        query_set = super().get_queryset()
        request = self.context.get('request')
        project = request.parser_context['kwargs']['parent_lookup_project']
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
        fields = ('pk', 'name', 'env_vars')


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
    environments = PrimaryKeyRelatedFieldByProject(queryset=models.Environment.objects.all(),
                                                   many=True,
                                                   required=False)

    class Meta:
        model = models.Pipeline
        depth = 2
        fields = ('pk', 'name', 'stages', 'environments')


class ProjectSerializer(serializers.ModelSerializer):
    environments = serializers.PrimaryKeyRelatedField(queryset=models.Environment.objects.all(),
                                                      many=True,
                                                      required=False)

    class Meta:
        model = models.Project
        fields = ('pk', 'name', 'environments')
