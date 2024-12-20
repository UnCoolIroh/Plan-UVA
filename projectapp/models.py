import os
import boto3
import mimetypes
from django.conf import settings
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

s3_client = boto3.client('s3')

class Keyword(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Project_user(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=20)
    real_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, default="COMMON")
    inbox = models.CharField(max_length=20000) # string, representing a json array of message objects
    projects = models.CharField(max_length=20000) # string, representing a json array of project objects
    keywords = models.ManyToManyField(Keyword, related_name='project_users', blank=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    join_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    def __str__(self):
        return self.real_name or self.user.username or self.file_name
    
    def get_username(self):
        return self.username
    
    def get_role(self):
        return self.role

    def get_inbox(self):
        #TODO: add inplementation to convert json string into array of messages
        return self.inbox
    
    def get_projects(self):
        #TODO: add inplementation to convert json string into array of projects
        return self.projects

    def is_admin(self):
        return self.role == "ADMIN"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
    
    
@receiver(post_save, sender=User)
def create_project_user(sender, instance, created, **kwargs):
    if created:
        Project_user.objects.create(user=instance, username=instance.username, email=instance.email)

@receiver(post_save, sender=User)
def save_project_user(sender, instance, **kwargs):
    instance.project_user.save()


class Project_group(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    owner = models.ForeignKey(Project_user, on_delete=models.CASCADE, related_name='owned_projects', null=True, blank=True)
    members = models.ManyToManyField(Project_user, related_name='project_groups')
    def __str__(self):
        return f"{self.name}"

    def has_requested(self, project_user):
        return self.join_requests.filter(user=project_user, approved=False, rejected=False).exists()

    def is_member(self, project_user):
        return self.members.filter(id=project_user.id).exists()

    def get_progress(self):
        tasks = self.tasks.all()
        total_weight = 0
        completed_weight = 0 
        for task in tasks:
            total_weight += task.weight
            if task.is_complete:
                completed_weight += task.weight
        if total_weight == 0:
            return 0
        progress_percent = (completed_weight / total_weight) * 100 
        return round(progress_percent)

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_group = models.ForeignKey(
        'Project_group', on_delete=models.CASCADE, related_name='documents', null=True, blank=True
    )
    file = models.FileField(upload_to='uploads/', null=True, blank=True)  # Add this field
    file_name = models.CharField(max_length=255, null=True, blank=True)
    uploaded_time = models.DateTimeField(auto_now_add=True)
    keywords = models.ManyToManyField('Keyword', related_name='document_keywords', blank=True)
    s3_file_name = models.CharField(max_length=255, null=True, blank=True)
    file_extension = models.CharField(max_length=15, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.file_name
    
    def download_url(self):
    # Generate URL for download (forces download)
        return s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'swe-vincent-test',
                'Key': self.s3_file_name,
                'ResponseContentDisposition': 'attachment'
            }
        )
    
    def preview_url(self):
        # Generate URL for preview (inline display)
        return s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'swe-vincent-test',
                'Key': self.s3_file_name,
                'ResponseContentDisposition': 'inline'
            }
        )
    
    def save(self, *args, **kwargs):
        if not self.pk:  
            super().save(*args, **kwargs)
            self.s3_file_name = f"{self.id}_{os.path.basename(self.file_name)}"
            return
        super().save(*args, **kwargs)

    def generate_s3_url(self):
        client = boto3.client('s3')
        url = client.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': self.s3_file_name})
        return url
    
    def content_type(self):
        if(self.file_extension == 'txt'):
            return 'text/plain'
        return f'application/{self.file_extension}'

class Conversation(models.Model):
    participants = models.ManyToManyField(Project_user, related_name='conversations')
    is_DM = models.BooleanField(default=False)
    project_group = models.ForeignKey('Project_group', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    def __str__(self):
        if self.is_DM:
            # Assuming we want to display the usernames of the participants for DMs
            participants_list = " and ".join([user.username for user in self.participants.all()])
            return f"DM between {participants_list}"
        else:
            if self.project_group:
                return f"Conversation for {self.project_group.name}"
            return f"no project group assigned"
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    document = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.document:
            return f"{self.sender.username}: {self.text} (File attached: {self.document.file_name})"
        return f"{self.sender.username}: {self.text}"

class JoinRequest(models.Model):
    user = models.ForeignKey(Project_user, on_delete=models.CASCADE)
    group = models.ForeignKey(Project_group, on_delete=models.CASCADE, related_name='join_requests')
    timestamp = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} requests to join {self.group.name}"


class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True) 
    project_group = models.ForeignKey(Project_group, on_delete=models.CASCADE, related_name='tasks') 
    assigned_users = models.ManyToManyField(User, related_name='tasks', blank=True) 
    weight = models.PositiveIntegerField(default=0) 
    is_complete = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Task: {self.name}, Status: {self.status}, Due: {self.due_date}"

    def is_overdue(self):
        return self.due_date < timezone.now() and not self.is_complete
    
    def clean(self):
        if self.weight > 10:
            raise ValidationError({'weight': 'Weight cannot be more than 10.'})