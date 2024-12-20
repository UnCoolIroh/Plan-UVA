import os
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from ..models import Project_user, Document, Project_group, Conversation
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from django.contrib.sites.models import Site

class ViewsTest(TestCase):
    def setUp(self):
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        name = "Google"
        
        if not SocialApp.objects.filter(provider='google', client_id=client_id).exists():
            app = SocialApp.objects.create(
                provider='google',
                name=name,
                client_id=client_id,
                secret=secret
            )
            app.sites.add(Site.objects.get_current())
            app.save()

        self.client = Client()
        self.user = User.objects.create_user(username='testuser5', password='testpass', email='testemail@gmail.com')
        
        self.project_user = self.user.project_user #made by signal emitted by creation of user 

        self.project_user.real_name = 'Test User 5'
        self.project_user.save()
        self.client.login(username='testuser5', password='testpass')

    def test_home_view_authenticated(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('common_user_dashboard'))

    def test_home_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_common_user_dashboard_view(self):
        response = self.client.get(reverse('common_user_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'common_user_dashboard.html')

    def test_pma_admin_dashboard_view(self):
        self.project_user.role = 'ADMIN'
        self.project_user.save()
        response = self.client.get(reverse('pma_admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pma_admin_dashboard.html')


    #def test_uploaded_files_view(self):
        #response = self.client.get(reverse('uploaded_files'))
        #self.assertEqual(response.status_code, 200)
        #self.assertTemplateUsed(response, 'uploaded_files.html')


    def test_project_group_view(self):
        project_group = Project_group.objects.create(name='Test Group3', description='Test Description', owner=self.project_user)
        project_group.members.add(self.project_user)
        response = self.client.get(reverse('project_group', args=[project_group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_group.html')

    def test_conversation_view(self):
        project_group = Project_group.objects.create(name='Test Group4', description='Test Description')
        conversation = Conversation.objects.create(project_group=project_group)
        response = self.client.get(reverse('conversation', args=[conversation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'conversation.html')
