from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from api import models


@admin.register(models.Account)
class AccountAdmin(GuardedModelAdmin):
    pass


@admin.register(models.Project)
class ProjectAdmin(GuardedModelAdmin):
    list_display = ['name', 'account']


@admin.register(models.Environment)
class EnvironmentAdmin(GuardedModelAdmin):
    pass


@admin.register(models.Pipeline)
class PipelineAdmin(GuardedModelAdmin):
    pass


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
    fields = ["url"]
    list_display = ["url"]
    inlines = [ScmWebhookAdmin, ScmPollAdmin]


@admin.register(models.Artifact)
class ArtifactAdmin(GuardedModelAdmin):
    pass


@admin.register(models.Stage)
class StageAdmin(GuardedModelAdmin):
    filter_horizontal = ['environments']
