from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Project_user, Project_group, Conversation
from django.urls import reverse

class ConversationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='testpass', email='testemail@gmail.com')
        self.project_user = self.user.project_user
        self.project_user.real_name = 'Test User 2'
        self.project_user.save()
        
        self.user2 = User.objects.create_user(username='testuser3', password='testpass', email='testemail2@gmail.com')
        self.project_user2 = self.user2.project_user
        self.project_user2.real_name = 'Test User 3'
        self.project_user2.save()
        
        self.conversation = Conversation.objects.create(is_DM = True)
        self.conversation.participants.add(self.project_user)
        self.conversation.participants.add(self.project_user2)
        
        self.client.login(username='testuser2', password='testpass')

    def test_conversation_creation(self):
        self.assertIn(self.project_user, self.conversation.participants.all())


    def test_leave_conversation(self):
        #leaving a conversation should remove the participant from that conversation's participant list 
        response = self.client.post(reverse('delete_conversation', kwargs={'conversation_id': self.conversation.id}))
        self.conversation.refresh_from_db()
        self.assertNotIn(self.project_user, self.conversation.participants.all())

    def test_delete_conversation(self):
        #if the last participant leaves, the conversation should be deleted 
        solo_conversation = Conversation.objects.create(is_DM=True)
        solo_conversation.participants.add(self.project_user)
        
        response = self.client.post(reverse('delete_conversation', kwargs={'conversation_id': solo_conversation.id}))
        self.assertRedirects(response, reverse('common_user_dashboard'))
        
        with self.assertRaises(Conversation.DoesNotExist):
            Conversation.objects.get(id=solo_conversation.id)