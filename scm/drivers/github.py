import hashlib
import hmac

from scm.drivers import SCMDriver


def _sign_request(body, secret):
    signature = 'sha1=' + hmac.new(
        secret.encode('utf-8'), body, hashlib.sha1).hexdigest()
    return signature


class GithubDriver(SCMDriver):
    def associate_pipelines(self, request):
        pass

    def trigger_pipeline_run(self, pipelines):
        pass

    def poll_repo(self, repo):
        pass

    def validate_webhook(self):
        pass
