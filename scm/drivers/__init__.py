import abc
import json
import pkgutil

from scm.models import Repo


class SCMManager:
    driver_map = {}

    def _associate_driver(self, headers):
        for identifier in self.driver_map:
            if identifier in headers:
                return self.driver_map[identifier]

    def get_pipelines(self, request):
        driver = self._associate_driver(request.headers)(request)
        driver.validate_webhook()
        user = driver.get_user()
        repo = driver.get_repo()
        branch = driver.get_branch()
        # (^|,) Matches either start of string, or comma
        # (,|$) Matches either end of string, or comma
        # For comma separated list, match any component
        regex = r'(^|,){0}(,|$)'.format(branch)
        pipelines = Repo.objects.filter(branch__iregex=regex)
        return pipelines

    def trigger_pipeline(self, pipelines, user):
        a = self.driver_map
        print(pipelines)


class SCMDriver(abc.ABC):
    format = ''
    identifier = ''

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        SCMManager.driver_map[cls.identifier] = cls

    def __init__(self, request=None):
        if request:
            self.request_body = json.loads(request.body)
            self.request_headers = request.headers

    @abc.abstractmethod
    def get_user(self):
        """
        Finds user associated with webhook event
        :return: str
        """
        pass

    @abc.abstractmethod
    def get_repo(self):
        """
        Finds repo associated with webhook event
        :return: str
        """
        pass

    @abc.abstractmethod
    def get_branch(self):
        """
        Finds branch associated with webhook event
        :return: str
        """

    @abc.abstractmethod
    def poll_repo(self, repo):
        """
        Poll specified repo
        :param str repo: Repository to poll
        :return:
        """
        pass

    @abc.abstractmethod
    def validate_webhook(self):
        """
        Validate webhook matches expected schema.
        :return: bool
        """
        pass


__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module
