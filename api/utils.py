from uuid import uuid4

from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

from api import models


def initialize_account(user, obj):
    for grp in ['owner', 'admin', 'users']:
        g = Group.objects.create(name=str(uuid4()))
        agm = models.AccountGroupMapping.objects.create(name=f'account-{grp}', grp=g, account=obj)
        user.groups.add(agm.grp)
        if grp == 'owner':
            assign_perm('api.view_finance', g, obj)
        elif grp == 'admin':
            assign_perm('api.change_account', g, obj)
            assign_perm('api.view_account', g, obj)
            assign_perm('api.delete_account', g, obj)
            assign_perm('api.add_account_users', g, obj)
            assign_perm('api.add_project', g)
            assign_perm('api.delete_project', g)
            assign_perm('api.view_project', g)
        else:
            assign_perm('api.view_account', g, obj)


def add_project_perms(user, obj):
    account = obj.account
    project_name = obj.name

    account_admin = models.AccountGroupMapping.objects.get(name='account-admin', account=account)
    assign_perm('api.delete_project', account_admin.grp, obj)

    for grp in ['admin', 'run']:
        g = Group.objects.create(name=str(uuid4()))
        agm = models.AccountGroupMapping.objects.create(name=f'{account.name}-{project_name}-{grp}',
                                                        grp=g,
                                                        account=account)
        user.groups.add(agm.grp)

        if grp == 'admin':
            assign_perm('api.change_project', g, obj)
            assign_perm('api.add_project_users', g, obj)
            assign_perm('api.view_project', g, obj)
            assign_perm('api.add_environment', g)
            assign_perm('api.delete_environment', g)
            assign_perm('api.add_pipeline', g)
            assign_perm('api.delete_pipeline', g)
        else:
            assign_perm('run_pipeline', g, obj)


def add_perms(obj):
    account = obj.project.account
    project_name = obj.project.name
    obj_type = type(obj).__name__.lower()
    adm_group = models.AccountGroupMapping.objects.get(name=f'{account.name}-{project_name}-admin', account=account)
    for perm in ['view', 'change', 'delete']:
        assign_perm(f'api.{perm}_{obj_type}', adm_group.grp, obj)
        print(f'api.{perm}_{obj_type}')

    run_group = models.AccountGroupMapping.objects.get(name=f'{account.name}-{project_name}-run', account=account)
    assign_perm(f'api.view_{obj_type}', run_group.grp, obj)
