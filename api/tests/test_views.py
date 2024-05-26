from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from api import models


class AccountViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User, username='private')

    def setUp(self):
        self.user = baker.make(models.User, username='user1')

    def test_user_can_only_view_their_accounts(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:account-list'), format='json', follow=True)
        response.render()
        self.assertIn({'name': 'user1'}, response.data['results'])
        self.assertNotIn({'name': 'private'}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)

    def test_anonymous_user_has_no_permissions(self):
        response = self.client.get(reverse('api:account-list'), follow=True)
        response.render()
        self.assertEqual(response.status_code, 403)


class ProjectViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User, username='private')
        baker.make(models.Project, name='private_project')

    def setUp(self):
        self.user = baker.make(models.User, username='user1')

    def test_user_list_acct_project(self):
        """
        Test that a logged-in user can only view projects in his own account.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:project-list', kwargs={'account': 'user1'}), follow=True)
        response.render()
        self.assertIn({"name": "default", "environments": [], "pipelines": []}, response.data['results'])
        self.assertNotIn({"name": "private_project",
                          "environments": [],
                          "pipelines": []},
                         response.data['results'])
        self.assertEqual(len(response.data['results']), 1)

    def test_user_cannot_view_private_projects(self):
        """
        Test user cannot view projects associated with another account
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:project-list', kwargs={'account': 'private'}), follow=True)
        self.assertNotIn({"name": "private_project",
                          "environments": [],
                          "pipelines": []},
                         response.data['results'])
        self.assertEqual(response.status_code, 404)

    def test_project_create(self):
        """
        Test that an authorized user can create a new project in his account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:project-list', kwargs={'account': 'user1'}),
                                    data={"name": "project1", "pipelines": [], "environments": []},
                                    headers={"content-type": "application/json"},
                                    follow=True)
        response.render()
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_project_cannot_create_unauthorized_account(self):
        """
        Test that an authorized user cannot create a new project in another account.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse('api:project-list', kwargs={'account': 1}),
                                    {"name": "project1"}, headers={"content-type": "application/json"},
                                    follow=True)
        response.render()
        self.assertEqual(response.status_code, 404)

    def test_project_delete(self):
        """
        Test that an authorized user can delete a project in his account.
        """
        self.client.force_login(self.user)
        post_response = self.client.post(reverse('api:project-list', kwargs={'account': 2}),
                                         {"name": "project1"}, headers={"content-type": "application/json"},
                                         follow=True)
        post_response.render()
        pk = post_response.data['pk']
        response = self.client.delete(reverse('api:project-detail',
                                              kwargs={'account': 2, 'pk': pk}))
        self.assertEqual(response.status_code, 204)

    def test_anonymous_permissions(self):
        """
        Test that an anonymous user cannot view any projects.
        """
        response = self.client.get(reverse('api:project-list', kwargs={'account': 1}), follow=True)
        response.render()
        self.assertEqual(response.status_code, 403)


class EnvironmentViewSetTest(APITestCase):
    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.client.force_login(self.user)
        self.client.post(reverse('api:environment-list',
                                 kwargs={'account': 'user1', 'project': 'default'}),
                         {"name": "env1"}, headers={"content-type": "application/json"},
                         follow=True)

    def test_user_can_view_environment(self):
        """
        Test that an authorized user can view an environment in his account.
        """
        response = self.client.get(reverse('api:environment-detail',
                                           kwargs={'account': "user1",
                                                   'project': 'default',
                                                   'pk': 1}),
                                   follow=True)
        self.assertEqual({"pk": 1, "name": "env1", "env_vars": []}, response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_environment(self):
        """
        Test that an authorized user can delete an environment in his account
        """
        response = self.client.delete(reverse('api:environment-detail',
                                              kwargs={'account': "user1",
                                                      'project': 'default',
                                                      'pk': 1}),
                                      follow=True)
        self.assertEqual(response.status_code, 204)


class PipelineViewSetTest(APITestCase):
    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.stage = {"name": "stage1", "jobs": [{"name": "job1"}, {"name": "job2"}]}
        self.client.force_login(self.user)
        self.client.post(reverse('api:pipeline-list',
                                 kwargs={'account': "user1", 'project': 'default'}),
                         {"name": "pipeline1", "stages": [self.stage]}, headers={"content-type": "application/json"},
                         follow=True)

    def test_user_can_create_pipeline(self):
        """
        Test that an authorized user can view a pipeline in his account.
        """
        response = self.client.get(reverse('api:pipeline-detail',
                                           kwargs={'account': "user1",
                                                   'project': 'default',
                                                   'pk': 1}),
                                   follow=True)
        self.assertEqual({"pk": 1, "name": "pipeline1", "stages": [self.stage], "environments": []}, response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_pipeline(self):
        """
        Test that an authorized user can delete a pipeline in his account.
        """
        response = self.client.delete(reverse('api:pipeline-detail',
                                              kwargs={'account': "user1",
                                                      'project': 'default',
                                                      'pk': 1}),
                                      follow=True)
        self.assertEqual(response.status_code, 204)


class RunPipelineTest(APITestCase):
    pass
