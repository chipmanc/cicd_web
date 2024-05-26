from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient, APITestCase

from api import models


class AccountViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User)

    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.c = APIClient()

    def test_user_can_only_view_their_accounts(self):
        self.c.force_login(self.user)
        response = self.c.get(reverse('api:account-list'), format='json')
        response.render()
        self.assertIn({'name': 'user1'}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)

    def test_anonymous_user_has_no_permissions(self):
        response = self.c.get(reverse('api:account-list'))
        response.render()
        self.assertEqual(response.status_code, 403)


class ProjectViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User)

    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.c = APIClient()

    def test_user_list_acct_project(self):
        """
        Test that a logged-in user can only view projects in his own account.
        """
        self.c.force_login(self.user)
        response = self.c.get(reverse('api:project-list', kwargs={'account': 2}))
        response.render()
        self.assertNotIn({"account": 1, "name": "default"}, response.data['results'])
        self.assertIn({"pk": 2, "name": "default", "environments": []}, response.data['results'])

    def test_project_create(self):
        """
        Test that an authorized user can create a new project in his account.
        """
        self.c.force_login(self.user)
        response = self.c.post(reverse('api:project-list', kwargs={'account': 2}),
                               {"name": "project1"}, headers={"content-type": "application/json"})
        response.render()
        self.assertEqual(response.status_code, 201)

    def test_project_cannot_create_unauthorized_account(self):
        """
        Test that an authorized user cannot create a new project in another account.
        """
        self.c.force_login(self.user)
        response = self.c.post(reverse('api:project-list', kwargs={'account': 1}),
                               {"name": "project1"}, headers={"content-type": "application/json"})
        response.render()
        self.assertEqual(response.status_code, 404)

    def test_project_delete(self):
        """
        Test that an authorized user can delete a project in his account.
        """
        self.c.force_login(self.user)
        post_response = self.c.post(reverse('api:project-list', kwargs={'account': 2}),
                                    {"name": "project1"}, headers={"content-type": "application/json"})
        post_response.render()
        pk = post_response.data['pk']
        response = self.c.delete(reverse('api:project-detail',
                                         kwargs={'account': 2, 'pk': pk}))
        self.assertEqual(response.status_code, 204)

    def test_anonymous_permissions(self):
        """
        Test that an anonymous user cannot view any projects.
        """
        response = self.c.get(reverse('api:project-list', kwargs={'account': 1}))
        response.render()
        self.assertEqual(response.status_code, 403)


class EnvironmentViewSetTest(APITestCase):
    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.c = APIClient()
        self.c.force_login(self.user)
        self.c.post(reverse('api:environment-list',
                            kwargs={'project__account': 1, 'project': 1}),
                    {"name": "env1"}, headers={"content-type": "application/json"})

    def test_user_can_view_environment(self):
        """
        Test that an authorized user can view an environment in his account.
        """
        response = self.c.get(reverse('api:environment-detail',
                                      kwargs={'project__account': 1,
                                              'project': 1,
                                              'pk': 1}))
        self.assertEqual({"pk": 1, "name": "env1", "env_vars": []}, response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_environment(self):
        """
        Test that an authorized user can delete an environment in his account
        """
        response = self.c.delete(reverse('api:environment-detail',
                                         kwargs={'project__account': 1,
                                                 'project': 1,
                                                 'pk': 1}))
        self.assertEqual(response.status_code, 204)


class PipelineViewSetTest(APITestCase):
    def setUp(self):
        self.user = baker.make(models.User, username='user1')
        self.c = APIClient()
        self.stage = {"name": "stage1", "jobs": [{"name": "job1"}, {"name": "job2"}]}
        self.c.force_login(self.user)
        self.c.post(reverse('api:pipeline-list',
                            kwargs={'project__account': 1, 'project': 1}),
                    {"name": "pipeline1", "stages": [self.stage]}, headers={"content-type": "application/json"})

    def test_user_can_create_pipeline(self):
        """
        Test that an authorized user can view a pipeline in his account.
        """
        response = self.c.get(reverse('api:pipeline-detail',
                                      kwargs={'project__account': 1,
                                              'project': 1,
                                              'pk': 1}))
        self.assertEqual({"pk": 1, "name": "pipeline1", "stages": [self.stage], "environments": []}, response.data)
        self.assertEqual(response.status_code, 200)

    def test_user_can_delete_pipeline(self):
        """
        Test that an authorized user can delete a pipeline in his account.
        """
        response = self.c.delete(reverse('api:pipeline-detail',
                                         kwargs={'project__account': 1,
                                                 'project': 1,
                                                 'pk': 1}))
        self.assertEqual(response.status_code, 204)


class RunPipelineTest(APITestCase):

    pass
