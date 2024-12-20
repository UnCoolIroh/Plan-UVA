from django.test import TestCase, Client
from django.urls import reverse
from ..views import *
from ..models import *

class DocumentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser4', password='testpass', email='testemail@gmail.com')
        self.user2 = User.objects.create_user(username='testuser5', password='testpass', email='testemail2@gmail.com')
        
        self.project_user = self.user.project_user
        self.project_user2 = self.user2.project_user

        self.conversation = Conversation.objects.create()
        self.conversation2 = Conversation.objects.create()
        self.common_group = Conversation.objects.create()

        self.conversation.participants.add(self.project_user)
        self.conversation2.participants.add(self.project_user2)
        self.common_group.participants.add(self.project_user)
        self.common_group.participants.add(self.project_user2)

        self.document = Document.objects.create(user=self.user, file_name='testfile1.txt')
        self.document2 = Document.objects.create(user=self.user2, file_name='testfile2.txt')
        self.document3 = Document.objects.create(user=self.user2, file_name='testfile3.txt')

        self.keyword = Keyword.objects.create(name='testkeyword')
        self.keyword2 = Keyword.objects.create(name='otherkeyword')
        self.keyword3 = Keyword.objects.create(name='thirdkeyword')

        self.document.keywords.add(self.keyword)
        self.document2.keywords.add(self.keyword2)
        self.document3.keywords.add(self.keyword3)

        self.message = Message.objects.create(sender= self.project_user.user, document=self.document, text='Test message 1', conversation=self.conversation)
        self.message2 = Message.objects.create(sender= self.project_user2.user, document=self.document2, text='Test message 2', conversation=self.conversation2)
        self.message3 = Message.objects.create(sender= self.project_user2.user, document=self.document3, text='test message 3', conversation=self.common_group)

        self.client = Client()
        self.client.login(username='testuser4', password='testpass')

    def test_document_creation(self):
        self.assertEqual(self.document.user.username, 'testuser4')
        self.assertEqual(self.document.file_name, 'testfile1.txt')

    def test_document_search(self):
        result = query_documents(self.project_user,'testkeyword')
        self.assertIn(self.document, result['documents'])

    def test_search_shows_documents_from_groups(self):
        # Search results should show documents that other people uploaded, as long as they are from groups the user is in
        result = query_documents(self.project_user,'thirdkeyword')
        self.assertIn(self.document3, result['documents'])

    def test_search_does_not_show_documents_from_other_groups(self):
        # Search results should not show documents uploaded to groups the user is not in
        result = query_documents(self.project_user,'otherkeyword')
        self.assertNotIn(self.document2, result['documents'])