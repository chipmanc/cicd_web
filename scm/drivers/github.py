import hashlib
import hmac
import json

from scm.drivers import SCMDriver


def _sign_request(body, secret):
    signature = 'sha1=' + hmac.new(
        secret.encode('utf-8'), body, hashlib.sha1).hexdigest()
    return signature


class GithubDriver(SCMDriver):
    format = 'github'
    identifier = 'X-GitHub-Delivery'

    def __init__(self, request=None):
        if request:
            self.request_body = json.loads(request.body)

    def get_user(self):
        if self.request_body:
            return self.request_body['sender']['login']

    def get_repo(self):
        if self.request_body:
            return self.request_body['repository']['full_name']

    def get_branch(self, request=None):
        if self.request_body:
            return self.request_body['ref']

    def poll_repo(self, repo):
        pass

    def validate_webhook(self):
        pass
