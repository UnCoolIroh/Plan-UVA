from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Project_user, Project_group, Conversation, Message

class MessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser3', password='testpass', email='testemail@gmail.com')
        self.project_user = self.user.project_user
        self.project_user.real_name = 'Test User 3'
        self.project_user.save()
        self.project_group = Project_group.objects.create(name='Test Group2', description='Test Description')
        self.conversation = Conversation.objects.create(project_group=self.project_group)
        self.conversation.participants.add(self.project_user)
        self.message = Message.objects.create(sender=self.user, text='Test Message1', conversation=self.conversation)

    def test_message_creation(self):
        self.assertEqual(self.message.sender.username, 'testuser3')
        self.assertEqual(self.message.text, 'Test Message1')
        self.assertEqual(self.message.conversation, self.conversation)
