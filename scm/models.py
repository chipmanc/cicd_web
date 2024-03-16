from django.db import models
from encrypted_model_fields.fields import EncryptedCharField


class Repo(models.Model):
    FETCH_TYPE = [
        ('poll', 'Poll for changes'),
        ('webhook', 'Use webhook to listen for changes')
    ]
<<<<<<< Updated upstream
    url = models.URLField()
    user = models.CharField(max_length=50)
    branch = models.CharField(max_length=255, default='master', blank=True)
    shallow_clone = models.BooleanField(default=False)
    fetch = models.CharField(max_length=4, choices=FETCH_TYPE, default='poll')
=======
    fetch = models.CharField(max_length=7, choices=FETCH_TYPE, default='poll')
    shallow_clone = models.BooleanField(default=False)
    url = models.URLField()
    user = models.CharField(max_length=50)
    webhook_secret = EncryptedCharField(max_length=255, null=True, blank=True)


class Branch(models.Model):
    name = models.CharField(max_length=255)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE, related_name='branch')

>>>>>>> Stashed changes
