from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import add_project_perms, initialize_account


# Execution App
class Account(models.Model):
    payment = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=255, primary_key=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        permissions = [
            ('view_finance', 'Can view payment information'),
            ('add_account_users', 'Can add users to account'),
        ]


class Project(models.Model):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='projects', editable=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'account')
        permissions = [
            ("add_project_users", "Can add users to project"),
            ("run_pipeline", "Can run pipeline"),
        ]


class Environment(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='environments')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'project')


class EnvVar(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='env_vars')

    def __str__(self):
        return self.key

    class Meta:
        unique_together = ('key', 'environment')


class Stage(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stages')
    environments = models.ManyToManyField(Environment)
    manual_trigger = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'project')


class Pipeline(models.Model):
    name = models.CharField(max_length=255)
    environments = models.ManyToManyField(Environment)
    stages = models.ManyToManyField(Stage, related_name='pipelines')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'project')


class Task(models.Model):
    name = models.CharField(max_length=255)
    command = models.TextField()
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'stage')


# Trigger app
class Trigger(models.Model):
    TRIGGER_TYPE = [
        ('artifact', 'Artifact'),
        ('git', 'Git'),
        ('manual', 'Manual'),
        ('secret', 'Secret')
    ]
    name = models.CharField(max_length=255, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='triggers')
    trigger_type = models.CharField(max_length=25, choices=TRIGGER_TYPE)


class Git(models.Model):
    FETCH_TYPE = [
        ('poll', 'Poll'),
        ('webhook', 'Webhook')
    ]
    fetch = models.CharField(max_length=15, choices=FETCH_TYPE, default='poll')
    trigger = models.OneToOneField(Trigger, on_delete=models.CASCADE, related_name='git')
    url = models.URLField()


class ScmWebhook(models.Model):
    git = models.OneToOneField(Git, on_delete=models.CASCADE, related_name='webhook')
    webhook_secret = models.CharField(max_length=255, null=True, blank=True)


class ScmPoll(models.Model):
    branch = models.CharField(max_length=255, default='master')
    git = models.OneToOneField(Git, on_delete=models.CASCADE, related_name='poll')
    shallow_clone = models.BooleanField(default=False)
    user = models.CharField(max_length=50)


# API
class User(AbstractUser):
    email = models.EmailField(max_length=255, blank=False)

    def __str__(self):
        return f'{self.username}'


@receiver(post_save, sender=User)
def user_creation(instance, created, **kwargs):
    if created:
        account = Account.objects.create(default=False, name=instance.username)
        project = Project.objects.create(name='default', account=account)
        initialize_account(instance, account)
        add_project_perms(instance, project)
