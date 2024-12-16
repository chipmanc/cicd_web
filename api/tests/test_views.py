from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api import models


class AccountViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User, username='private')

    def setUp(self):
        self.user = baker.make(models.User, username='user1', password='password')

    def test_user_can_only_view_their_accounts(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:account-list'), format='json', follow=True, secure=True)
        self.assertIn({'name': 'user1'}, response.data['results'])
        self.assertNotIn({'name': 'private'}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)

    def test_anonymous_user_has_no_permissions(self):
        response = self.client.get(reverse('api:account-list'), follow=True, secure=True)
        self.assertEqual(response.status_code, 401)


class ProjectViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User, username='private')

    def setUp(self):
        self.user = models.User.objects.create_user(username="user1", password="password")
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={'username': "user1", 'password': "password"},
                                    format='json',
                                    headers={"content-type": "application/json"}
                                    )
        self.token = response.data['access']

    def test_create_project(self):
        """
        Test that an authorized user can create a new project in his account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:project-list'),
                                    data={"name": "project1", "pipelines": [], "environments": []},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(models.Project.objects.filter(account__name='user1')), 2)

    def test_list_projects(self):
        """
        Test that a logged-in user can only view projects in his own account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:project-list'),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True, secure=True)
        self.assertIn({"name": "default", "environments": [], "pipelines": []}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)

    def test_read_project(self):
        """
        Test that a logged-in user can retrieve detailed project view in his own account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:project-detail', kwargs={"name": "default"}),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True, secure=True)
        self.assertEqual(response.data, {'name': 'default', 'pipelines': [], 'environments': []})
        self.assertEqual(response.status_code, 200)

    def test_update_project(self):
        pass

    def test_delete_project(self):
        """
        Test that an authorized user can delete a project in his account.
        """
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:project-detail',
                                              kwargs={'name': 'default'}),
                                      headers={'authorization': f'Bearer {self.token}'},
                                      follow=True, secure=True)
        self.assertEqual(response.status_code, 204)

    def test_anonymous_list_projects(self):
        """
        Test that an anonymous user cannot list any projects.
        """
        response = self.client.get(reverse('api:project-list'), follow=True, secure=True)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_read_project(self):
        """
        Test that an anonymous user cannot retrieve detailed project view.
        """
        response = self.client.get(reverse('api:project-detail', kwargs={"name": "default"}),
                                   follow=True, secure=True)
        self.assertEqual(response.status_code, 401)


class EnvironmentViewSetTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(username="user1", password="password")
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={'username': "user1", 'password': "password"},
                                    format='json',
                                    headers={"content-type": "application/json"}
                                    )
        self.token = response.data['access']
        self.client.post(reverse('api:environment-list'),
                         data={"name": "env1", "env_vars": {"key": "value"}},
                         headers={'authorization': f'Bearer {self.token}'},
                         follow=True,
                         secure=True
                         )

    def test_create_environment(self):
        """
        Test that an authorized user can create a new environment in his account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:environment-list'),
                                    data={"name": "env2", "env_vars": {"key": "value"}},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(models.Environment.objects.filter(project__account__name='user1')), 2)
        self.assertDictEqual(response.data['env_vars'], {"key": "value"})

    def test_list_environments(self):
        """
        Test that an authorized user can list environments in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:environment-list'),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertIn({"name": "env1", "env_vars": {"key": "value"}}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, 200)

    def test_read_environment(self):
        """
        Test that an authorized user can read environment in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:environment-detail', kwargs={"name": "env1"}),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertEqual(response.data, {'name': 'env1', 'env_vars': {'key': 'value'}})
        self.assertEqual(response.status_code, 200)

    def test_update_environment(self):
        pass

    def test_delete_environment(self):
        """
        Test that an authorized user can delete an environment in his account.
        """
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:environment-detail', kwargs={'name': 'env1'}),
                                      headers={'authorization': f'Bearer {self.token}'},
                                      follow=True,
                                      secure=True)
        self.assertEqual(response.status_code, 204)

    def test_anonymous_list_environments(self):
        """
        Test that an anonymous user cannot list any environments.
        """
        response = self.client.get(reverse('api:environment-list'), follow=True, secure=True)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_read_environment(self):
        """
        Test that an anonymous user cannot list any projects.
        """
        response = self.client.get(reverse('api:environment-detail', kwargs={"name": "env1"}),
                                   follow=True, secure=True)
        self.assertEqual(response.status_code, 401)


class PipelineViewSetTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(username="user1", password="password")
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={'username': "user1", 'password': "password"},
                                    format='json',
                                    headers={"content-type": "application/json"}
                                    )
        self.token = response.data['access']
        response = self.client.post(reverse('api:pipeline-list'),
                                    data={"name": "pipeline1"},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.pipeline = response.data

    def test_create_pipeline(self):
        """
        Test that an authorized user can create a new pipeline in his account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:pipeline-list'),
                                    data={"name": "pipeline2"},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(models.Pipeline.objects.filter(project__account__name='user1')), 2)

    def test_list_pipelines(self):
        """
        Test that an authorized user can list pipelines in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:pipeline-list'),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertIn(self.pipeline, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, 200)

    def test_read_pipeline(self):
        """
        Test that an authorized user can read pipeline in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:pipeline-detail', kwargs={"name": "pipeline1"}),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertEqual(response.data, self.pipeline)
        self.assertEqual(response.status_code, 200)

    def test_update_pipeline(self):
        pass

    def test_delete_pipeline(self):
        """
        Test that an authorized user can delete a pipeline in his account.
        """
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:pipeline-detail', kwargs={'name': 'pipeline1'}),
                                      headers={'authorization': f'Bearer {self.token}'},
                                      follow=True,
                                      secure=True)
        self.assertEqual(response.status_code, 204)

    def test_anonymous_list_pipeline(self):
        """
        Test that an anonymous user cannot list any pipelines.
        """
        response = self.client.get(reverse('api:pipeline-list'), follow=True, secure=True)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_read_pipeline(self):
        """
        Test that an anonymous user cannot list any pipelines.
        """
        response = self.client.get(reverse('api:pipeline-detail', kwargs={"name": "pipeline1"}),
                                   follow=True, secure=True)
        self.assertEqual(response.status_code, 401)


class StageViewSetTest(APITestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(username="user1", password="password")
        response = self.client.post(reverse('token_obtain_pair'),
                                    data={'username': "user1", 'password': "password"},
                                    format='json',
                                    headers={"content-type": "application/json"}
                                    )
        self.token = response.data['access']
        response = self.client.post(reverse('api:stage-list'),
                                    data={"name": "stage1", "tasks": [{"name": "task1", "command": "command1"}]},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.stage = response.data

    def test_create_stage(self):
        """
        Test that an authorized user can create a new stage in his account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:stage-list'),
                                    data={"name": "stage2"},
                                    headers={'authorization': f'Bearer {self.token}'},
                                    follow=True,
                                    secure=True
                                    )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(models.Stage.objects.filter(project__account__name='user1')), 2)

    def test_list_stages(self):
        """
        Test that an authorized user can list stages in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:stage-list'),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertIn(self.stage, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.status_code, 200)

    def test_read_stage(self):
        """
        Test that an authorized user can read stage in his account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:stage-detail', kwargs={"name": "stage1"}),
                                   headers={'authorization': f'Bearer {self.token}'},
                                   follow=True,
                                   secure=True
                                   )
        self.assertEqual(response.data, self.stage)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.data['tasks'], [{"name": "task1", "command": "command1"}])

    def test_update_stage(self):
        pass

    def test_delete_stage(self):
        """
        Test that an authorized user can delete a stage in his account.
        """
        self.client.force_login(self.user)
        response = self.client.delete(reverse('api:stage-detail', kwargs={'name': 'stage1'}),
                                      headers={'authorization': f'Bearer {self.token}'},
                                      follow=True,
                                      secure=True)
        self.assertEqual(response.status_code, 204)

    def test_anonymous_list_stage(self):
        """
        Test that an anonymous user cannot list any stages.
        """
        response = self.client.get(reverse('api:stage-list'), follow=True, secure=True)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_read_stage(self):
        """
        Test that an anonymous user cannot list any stages.
        """
        response = self.client.get(reverse('api:stage-detail', kwargs={"name": "stage1"}),
                                   follow=True, secure=True)
        self.assertEqual(response.status_code, 401)


class TriggerViewSetTest(APITestCase):
    pass
