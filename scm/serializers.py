from rest_framework import serializers

from scm import models


class GitRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repo
        fields = '__all__'
