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

    def _get_event(self):
        if self.request_headers:
            return self.request_headers['X-GitHub-Event']

    def get_user(self):
        if self.request_body:
            return self.request_body['sender']['login']

    def get_repo(self):
        if self.request_body:
            return self.request_body['repository']['full_name']

    def get_branch(self):
        if self.request_body:
            event = self._get_event()
            if event == 'push':
                return self.request_body['ref']
            elif event == 'pull_request':
                return self.request_body['pull_request']['base']['ref']

    def poll_repo(self, repo):
        pass

    def validate_webhook(self):
        pass
