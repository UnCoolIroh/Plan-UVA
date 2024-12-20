from django.test import TestCase, Client
from ..views import *
from ..models import *
class ProjectGroupModelTest(TestCase):
    def setUp(self):
        self.project_group = Project_group.objects.create(name='Test Group1', description='Test Description')

    def test_project_group_creation(self):
        self.assertEqual(self.project_group.name, 'Test Group1')
        self.assertEqual(self.project_group.description, 'Test Description')
