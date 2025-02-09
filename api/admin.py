from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from api import models


@admin.register(models.Account)
class AccountAdmin(GuardedModelAdmin):
    pass


@admin.register(models.Project)
class ProjectAdmin(GuardedModelAdmin):
    list_display = ['name', 'account']


@admin.register(models.EnvVar)
class EnvVarAdmin(GuardedModelAdmin):
    model = models.EnvVar


class EnvVar(admin.TabularInline):
    model = models.EnvVar


@admin.register(models.Environment)
class EnvironmentAdmin(GuardedModelAdmin):
    inlines = [EnvVar]


@admin.register(models.Pipeline)
class PipelineAdmin(GuardedModelAdmin):
    list_display = ['name', 'project', 'get_account_name']

    @admin.display(description='Account Name', ordering='account__name')
    def get_account_name(self, obj):
        return obj.project.account.name


@admin.register(models.Task)
class TaskAdmin(GuardedModelAdmin):
    pass


class ScmWebhookAdmin(admin.TabularInline):
    model = models.ScmWebhook
    pass


class ScmPollAdmin(admin.TabularInline):
    model = models.ScmPoll
    pass


@admin.register(models.Git)
class GitAdmin(GuardedModelAdmin):
    fields = ["name"]
    list_display = ["name"]
    inlines = [ScmWebhookAdmin, ScmPollAdmin]


@admin.register(models.Artifact)
class ArtifactAdmin(GuardedModelAdmin):
    pass


@admin.register(models.Stage)
class StageAdmin(GuardedModelAdmin):
    pass
