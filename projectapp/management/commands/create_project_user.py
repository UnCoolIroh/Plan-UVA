from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from projectapp.models import Project_user

class Command(BaseCommand):
    help = 'Create a Project_user linked to an existing User account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('password', type=str, help='Password of the user')
        parser.add_argument('real_name', type=str, help='Real name of the Project_user')
        parser.add_argument('email', type=str, help='Email of the Project_user')
        parser.add_argument('--role', type=str, default='COMMON', help='Role of the Project_user')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        real_name = kwargs['real_name']
        email = kwargs['email']
        role = kwargs['role']

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is None:
            self.stdout.write(self.style.ERROR('Authentication failed. Please check your credentials.'))
            return

        # Create Project_user
        project_user, created = Project_user.objects.get_or_create(
            user=user,
            defaults={
                'username': username,
                'real_name': real_name,
                'email': email,
                'role': role,
                'inbox': '[]',  # Empty JSON array as string
                'projects': '[]'  # Empty JSON array as string
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Project_user created: {project_user}'))
        else:
            self.stdout.write(self.style.WARNING('Project_user already exists for this user.'))