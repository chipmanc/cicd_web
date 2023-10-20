from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import add_project_perms, initialize_account


class Account(models.Model):
    payment = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=255)
    default = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    class Meta:
        permissions = [
            ('view_finance', 'Can view payment information'),
            ('add_account_users', 'Can add users to account'),
        ]


class AccountGroupMapping(models.Model):
    name = models.CharField(max_length=255)
    grp = models.OneToOneField(Group, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='groups')

    def __str__(self):
        return f'{self.account.name}-{self.name}'


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
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='env_vars')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'environment')


class Pipeline(models.Model):
    name = models.CharField(max_length=255)
    environments = models.ManyToManyField(Environment)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='pipelines')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'project')


class Stage(models.Model):
    name = models.CharField(max_length=255)
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='stages')
    manual_trigger = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Job(models.Model):
    name = models.CharField(max_length=255)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='jobs')

    def __str__(self):
        return self.name


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
