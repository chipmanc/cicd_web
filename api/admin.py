from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django_reverse_admin import ReverseModelAdmin
from guardian.admin import GuardedModelAdmin

from api import models


class AccountAdmin(GuardedModelAdmin):
    pass


class ProjectAdmin(GuardedModelAdmin):
    list_display = ['name', 'account']


class EnvironmentAdmin(GuardedModelAdmin):
    pass


class PipelineAdmin(GuardedModelAdmin):
    pass


class AGM(ReverseModelAdmin):
    list_display = ['name', 'account']
    inline_type = 'stacked'
    inline_reverse = [('grp', {'filter_horizontal': ['permissions'], 'fields': ['permissions']})]


admin.site.unregister(Group)
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Account, AccountAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.Environment, EnvironmentAdmin)
admin.site.register(models.Pipeline, PipelineAdmin)
admin.site.register(models.AccountGroupMapping, AGM)
