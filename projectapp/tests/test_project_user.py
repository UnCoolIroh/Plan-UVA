from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connection
from ..models import Project_user

class ProjectUserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser1', password='testpass', email='testemail@gmail.com')
        self.project_user = self.user.project_user
        self.project_user.real_name = 'Test User 1'
        self.project_user.save()

    def test_project_user_creation(self):
        self.assertEqual(self.project_user.username, 'testuser1')
        self.assertEqual(self.project_user.email, self.user.email)

    def test_get_username(self):
        self.assertEqual(self.project_user.username, 'testuser1')

    def test_get_role(self):
        self.assertEqual(self.project_user.role, 'COMMON')
