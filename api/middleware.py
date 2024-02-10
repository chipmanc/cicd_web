import re

from api import models


class InformationMiddleware:
    def __init__(self, get_response):
        self.project = None
        self.account = None
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        self.get_accounts(user, request)
        self.get_projects(user, request)
        self.get_environments(user, request)
        response = self.get_response(request)
        return response

    def get_accounts(self, user, request):
        agm = set()
        for g in user.groups.all():
            agm.add(models.AccountGroupMapping.objects.get(grp=g).account.name)
        request.session['accounts'] = list(agm)
        account_re = re.search('api/account/(?P<account>[^/.]+)/', request.path)
        if account_re:
            account = account_re.group('account')
            self.account = models.Account(pk=account)
        return

    def get_projects(self, user, request):
        project_list = list()
        try:
            projects = self.account.projects.all()
        except AttributeError:
            return
        for project in projects:
            if user.has_perm('api.view_project', project):
                project_list.append(project.name)
        request.session['projects'] = project_list
        project_re = re.search('api/account/[^/.]+/project/(?P<project>[^/.]+)/', request.path)
        if project_re:
            project = project_re.group('project')
            self.project = models.Project(pk=project)
        return

    def get_environments(self, user, request):
        environment_list = list()
        try:
            environments = self.project.environments.all()
        except AttributeError:
            return
        if user.has_perm('api.view_project', self.project):
            for environment in environments:
                environment_list.append(environment.name)
        request.session['environments'] = environment_list
        return
