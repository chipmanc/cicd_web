from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    token_class = RefreshToken

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(self.__dict__)
        self.fields["project"] = serializers.CharField(required=False, default="default")
        self.fields["account"] = serializers.CharField(required=False)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        if attrs.get("project", False):
            refresh["project"] = attrs["project"]
        if attrs.get("account", False):
            refresh["account"] = attrs["account"]
        data["refresh"] = str(refresh)
        data["access"] =  str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        return data

