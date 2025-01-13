from model_bakery import baker
from rest_framework.test import APITestCase

from api import models
from cicd.serializers import CustomTokenObtainPairSerializer


class PipelineSerializerTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(models.User, username='red_user')

    def setUp(self):
        self.user = baker.make(models.User, username='blue_user', password='password')

    def test_user_can_only_view_their_accounts(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('api:account-list'), format='json', follow=True, secure=True)
        self.assertIn({'name': 'blue_user'}, response.data['results'])
        self.assertNotIn({'name': 'red_user'}, response.data['results'])
        self.assertEqual(len(response.data['results']), 1)