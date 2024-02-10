import hashlib
import hmac

from scm.drivers import SCMDriver


def _sign_request(body, secret):
    signature = 'sha1=' + hmac.new(
        secret.encode('utf-8'), body, hashlib.sha1).hexdigest()
    return signature


class GithubDriver(SCMDriver):
    format = 'github'
    identifier = 'X-GitHub-Delivery'

    def get_user(self, request=None):
        if request:
            return request.body['sender']['login']

    def get_repo(self, request=None):
        if request:
            return request.body['repository']['full_name']

    def get_branch(self, request=None):
        if request:
            return request.body['ref']

    def poll_repo(self, repo):
        pass

    def validate_webhook(self):
        pass
