from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from guardian.admin import GuardedModelAdmin

from api import models


class AccountAdmin(GuardedModelAdmin):
    pass


class ProjectAdmin(GuardedModelAdmin):
    pass


class EnvironmentAdmin(GuardedModelAdmin):
    pass


class PipelineAdmin(GuardedModelAdmin):
    pass


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Environment, EnvironmentAdmin)
admin.site.register(models.Pipeline, PipelineAdmin)
admin.site.register(models.AccountGroupMapping)
