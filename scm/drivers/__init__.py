import abc


scm_registry = []


def register(cls):
    scm_registry.append(cls)


class SCMDriver(abc.ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print("I'm registered")
        register(cls)

    @abc.abstractmethod
    def associate_pipelines(self, request):
        """
        Takes a POST request from SCM source, parses it, and returns a list
        of pipelines configured with repo that triggered webhook
        :param django.http.request.HttpRequest request:
        :return: list
        """
        pass

    @abc.abstractmethod
    def trigger_pipeline_run(self, pipelines):
        """
        Sends API POST call to run pipelines
        :param list pipelines: List of pipelines to trigger
        :return: None
        """
        pass

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
