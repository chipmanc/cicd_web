from uuid import uuid4

from django.test import TestCase
from model_bakery import baker

from api import models


class AccountTestCase(TestCase):
    def setUp(self):
        self.account = baker.make(models.Account, name='account1')

    def test_acct_str(self):
        self.assertEqual(str(self.account), 'account1')


class EnvironmentTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.environment = baker.make(models.Environment, name='environment')

    def test_env_str(self):
        self.assertEqual(str(self.environment), 'environment')


class EnvVarTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.env_var = baker.make(models.EnvVar, name='envvar')

    def test_env_str(self):
        self.assertEqual(str(self.env_var), 'envvar')


class PipelineTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pipeline = baker.make(models.Pipeline, name='pipeline')

    def test_pipeline_str(self):
        self.assertEqual(str(self.pipeline), 'pipeline')


class StageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stage = baker.make(models.Stage, name='stage')

    def test_stage_str(self):
        self.assertEqual(str(self.stage), 'stage')


class JobTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.job = baker.make(models.Job, name='job')

    def test_job_str(self):
        self.assertEqual(str(self.job), 'job')


class ProjectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = baker.make(models.Project, name='project')

    def test_project_str(self):
        self.assertEqual(str(self.project), 'project')


class UserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = baker.make(models.User, username='user')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'user')
