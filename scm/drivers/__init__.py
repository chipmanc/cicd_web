import abc
import pkgutil

from scm.models import Repo


class SCMRegistry:
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
        pipelines = Repo.objects.filter(branch=branch)
        return pipelines

    def trigger_pipeline(self, pipelines, user):
        a = self.driver_map
        print(pipelines)


class SCMDriver(abc.ABC):
    format = ''
    identifier = ''

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        SCMRegistry.driver_map[cls.identifier] = cls

    @abc.abstractmethod
    def get_user(self, request):
        """
        Takes a webhook event and finds associated user
        :param django.http.request.HttpRequest request:
        :return: str
        """
        pass

    @abc.abstractmethod
    def get_repo(self, request):
        """
        Takes a webhook event and finds associated repo
        :param django.http.request.HttpRequest request:
        :return: str
        """
        pass

    @abc.abstractmethod
    def get_branch(self, request):
        """
        Takes a webhook event and finds associated branch
        :param django.http.request.HttpRequest request:
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
