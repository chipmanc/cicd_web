from django.db import models


class Repo(models.Model):
    FETCH_TYPE = [
        ('poll', 'Poll for changes'),
        ('push', 'Use webhook to listen for changes')
    ]
    url = models.URLField()
    user = models.CharField(max_length=50)
    branch = models.CharField(max_length=255, default='master', blank=True)
    shallow_clone = models.BooleanField(default=False)
    fetch = models.CharField(max_length=4, choices=FETCH_TYPE, default='poll')
