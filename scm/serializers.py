from rest_framework import serializers

from scm import models


class GitRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GitRepo
        fields = '__all__'
