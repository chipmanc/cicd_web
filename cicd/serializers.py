from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from api.models import Account, Project

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"] = serializers.CharField(required=False,
                                                       default="default")
        self.fields["account"] = serializers.CharField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        account_name = attrs.get("account", False)
        project_name = attrs.get("project", False)
        if account_name:
            account = Account.objects.get(name=account_name)
            if self.user.has_perm('api.view_account', account):
                refresh["account"] = account_name
            else:
                raise serializers.ValidationError("No account found")
        else:
            account_name = self.user.username
            refresh["account"] = account_name
        if project_name:
            project = Project.objects.get(name=project_name, account__name=account_name)
            if (self.user.has_perm('api.view_project', project)
                    and project.account.name == account_name):
                refresh["project"] = project_name
            else:
                raise serializers.ValidationError("No project found")
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

