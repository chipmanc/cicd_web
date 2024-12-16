from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
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
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.key

    class Meta:
        unique_together = ('key', 'environment')


class Stage(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stages')
    environments = models.ManyToManyField(Environment)
    manual_trigger = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'api'})
    object_id = models.PositiveIntegerField()
    trigger = GenericForeignKey("content_type", "object_id")

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

    def clean(self):
        self.command = self.command.replace('\r', '')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'stage')


class Git(models.Model):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='git')
    stage = GenericRelation(Stage, content_type_field='content_type',
                            object_id_field='object_id', related_query_name='git')

    def __str__(self):
        return self.url

    class Meta:
        verbose_name_plural = 'Git'


class ScmWebhook(models.Model):
    git = models.OneToOneField(Git, on_delete=models.CASCADE, related_name='webhook')
    webhook_secret = models.CharField(max_length=255, null=True, blank=True)


class ScmPoll(models.Model):
    branch = models.CharField(max_length=255, default='master')
    git = models.OneToOneField(Git, on_delete=models.CASCADE, related_name='poll')
    ref = models.CharField(max_length=64, null=True, blank=True)
    shallow_clone = models.BooleanField(default=False)
    user = models.CharField(max_length=50)


class Artifact(models.Model):
    stage = GenericRelation(Stage, content_type_field='content_type', object_id_field='object_id')


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
