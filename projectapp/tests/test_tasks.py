from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connection
from ..models import *
from ..views import *
class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser3', password='testpass', email='testemail@gmail.com')
        self.project_user = self.user.project_user

    def test_task_creation(self):
        pg = Project_group.objects.create(name='Test Group2', description='Test Description')
        task = Task.objects.create(name='task1', description='Task Description', weight=0, project_group = pg)
        self.assertEqual(task.name, 'task1')
        self.assertEqual(task.description, 'Task Description')
        self.assertEqual(task.weight, 0)
        self.assertEqual(task.project_group, pg)


    def test_progress_percentage(self):
        pg = Project_group.objects.create(name='Test Group2', description='Test Description')
        self.task2 = Task.objects.create(name='task2', description='Task Description', weight=1, project_group = pg)
        self.assertEqual(0, self.task2.project_group.get_progress())

    def test_progress_percentage_updates_on_task_completion(self):
        pg = Project_group.objects.create(name='Test Group2', description='Test Description')
        task = Task.objects.create(name='task2', description='Task Description', weight=1, project_group = pg)
        self.assertEqual(0, task.project_group.get_progress())
        task.is_complete = True
        task.save()
        self.assertEqual(100, task.project_group.get_progress())

    def test_progress_percentage_updates_on_task_deletion(self):
        pg = Project_group.objects.create(name='Test Group2', description='Test Description')
        task = Task.objects.create(name='task2', description='Task Description', weight=1, project_group = pg, is_complete=True)
        self.assertEqual(100, task.project_group.get_progress())
        task.delete()
        self.assertEqual(0, pg.get_progress())

    def test_assigned_user_leaves_group(self):
        pg = Project_group.objects.create(name='Test Group2', description='Test Description')
        task = Task.objects.create(name='task2', description='Task Description', weight=1, project_group = pg, is_complete=True)
        task.assigned_users.add(self.user)
        self.assertIn(self.user, task.assigned_users.all())
        remove_from_group(self.project_user, pg)
        self.assertNotIn(self.user, task.assigned_users.all())