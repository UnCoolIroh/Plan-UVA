from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib import messages
from .forms import *
from .models import *
from projectapp.models import *
import boto3
from django.db.models import Q
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)
def home(request):
    if not request.user.is_anonymous:
        # Check if the logged-in user is a Django admin (superuser)
        if request.user.is_superuser:
            return redirect('/admin/')  # Redirect to Django admin site

        # Get the Project_user instance
        project_user = get_project_user(request)

        # Redirect based on the user's role
        if project_user:
            if project_user.is_admin():  # PMA admin dashboard
                return redirect('pma_admin_dashboard')
            else:  # Common user dashboard
                return redirect('common_user_dashboard')

        # Fallback if no valid Project_user is found
        return redirect('home')

    # Render login/home page for unauthenticated users
    return render(request, 'home.html')

from django.contrib.auth.views import LoginView





def anon_dashboard(request):

    all_project_groups = Project_group.objects.all()
    context = {
        'all_project_groups': all_project_groups
    }
    return render(request, 'anon_dashboard.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')

def common_user_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)

    if project_user.role != 'COMMON':
        return redirect('pma_admin_dashboard')
    
    project_groups = project_user.project_groups.all()
    owned_projects = project_user.owned_projects.all()
    conversations = project_user.conversations.all()
    all_project_groups = Project_group.objects.exclude(members=project_user)

    groups_with_status = []
    for group in all_project_groups:
        has_requested = group.has_requested(project_user)
        groups_with_status.append({
            'group': group,
            'has_requested': has_requested,
        })

    context = {
        'project_user': project_user,
        'project_groups': project_groups,
        'owned_projects': owned_projects,
        'conversations': conversations,
        'all_project_groups': all_project_groups,
        'groups_with_status': groups_with_status,
    }
    return render(request, 'common_user_dashboard.html', context)

def pma_admin_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    if not project_user.is_admin():
        return redirect('common_user_dashboard')  # Redirect if not admin

    projects = Project_group.objects.all()

    files = Document.objects.all()

    messages_list = Message.objects.all()

    users = Project_user.objects.all()

    join_requests = JoinRequest.objects.all()

    context = {
        'project_user': project_user,
        'projects': projects,
        'files': files,
        'messages': messages_list,
        'users': users,
        'join_requests': join_requests,
    }
    return render(request, 'pma_admin_dashboard.html', context)

@login_required
def pma_admin_project_detail(request, project_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    if project_user.role != 'ADMIN':
        return redirect('common_user_dashboard')

    project = get_object_or_404(Project_group, id=project_id)
    messages_list = Message.objects.filter(conversation__project_group=project)
    documents = Document.objects.filter(project_group=project)

    context = {
        'project_user': project_user,
        'project': project,
        'messages': messages_list,
        'documents': documents,
    }
    return render(request, 'pma_admin_project_detail.html', context)

@login_required
def pma_admin_delete_project(request, project_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    if project_user.role != 'ADMIN':
        return redirect('common_user_dashboard')

    project = get_object_or_404(Project_group, id=project_id)

    if request.method == 'POST':
        # Initialize s3_client
        s3_client = boto3.client('s3')
        # Delete associated documents from S3 and the database
        for document in project.documents.all():
            # Delete from S3
            s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=document.s3_file_name
            )
            # Delete the document from the database
            document.delete()

        # Delete the project
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('pma_admin_dashboard')

    context = {
        'project_user': project_user,
        'project': project,
    }
    return render(request, 'pma_admin_delete_project.html', context)

@login_required
def pma_admin_delete_file(request, file_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    if project_user.role != 'ADMIN':
        return redirect('common_user_dashboard')

    document = get_object_or_404(Document, id=file_id)

    if request.method == 'POST':
        # Initialize s3_client
        s3_client = boto3.client('s3')
        # Delete from S3
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=document.s3_file_name
        )
        # Get project_group_id before deleting the document
        project_group_id = document.project_group.id if document.project_group else None

        # Delete the document from the database
        document.delete()
        messages.success(request, 'File deleted successfully.')

        # Redirect appropriately
        if project_group_id:
            return redirect('pma_admin_project_detail', project_id=project_group_id)
        else:
            return redirect('pma_admin_dashboard')

    context = {
        'project_user': project_user,
        'document': document,
    }
    return render(request, 'pma_admin_delete_file.html', context)


@login_required
def delete_file(request, file_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')

    document = get_object_or_404(Document, id=file_id)

    # Check if the user has permission to delete the file
    if document.user != request.user:
        messages.error(request, "You do not have permission to delete this file.")
        return redirect('common_user_dashboard')

    try:
        # Delete the file from S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        s3_client.delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=document.s3_file_name
        )

        # Delete the document from the database
        document.delete()

        # Provide user feedback
        messages.success(request, "File deleted successfully.")
    except Exception as e:
        # Handle any errors (e.g., S3 connection issues)
        messages.error(request, f"An error occurred while deleting the file: {e}")

    # Retrieve conversation_id and project_group_id from POST data
    conversation_id = request.POST.get('conversation_id')
    project_group_id = request.POST.get('project_group_id')

    # Redirect to the appropriate page
    if conversation_id:
        return redirect('conversation', id=conversation_id)
    elif project_group_id:
        return redirect('project_group', id=project_group_id)
    else:
        # Fallback: Redirect to common user dashboard
        return redirect('common_user_dashboard')

@login_required
def project_group(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    group = get_object_or_404(Project_group, id=id)
    conversation = group.conversations.first()  # Groups should only have one conversation
    project_user = get_project_user(request)
    is_member = group.is_member(project_user)
    is_owner = group.owner == project_user
    has_requested = group.has_requested(project_user) if not is_member else False
    progress_percent = group.get_progress()

    # Ensure only members can access the project
    if not is_member:
        return redirect('common_user_dashboard')

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        document_form = DocumentForm(request.POST, request.FILES)

        message = None
        document = None

        # Save the document if the form is valid and a file is provided
        if document_form.is_valid() and request.FILES.get('file'):
            file = request.FILES['file']
            file_name = document_form.cleaned_data.get('file_name', file.name)
            document = Document.objects.create(
                user=request.user,
                file_name=file_name,
                file_extension=file.name.split('.')[-1],
                description=document_form.cleaned_data.get('description', ''),
                s3_file_name=file.name,  # Replace with S3 handling if required
            )
            document.save()

            # Save keywords if provided
            keywords = document_form.cleaned_data.get('keywords', '')
            for keyword_name in keywords.split(','):
                keyword_name = keyword_name.strip()
                if keyword_name:
                    keyword, _ = Keyword.objects.get_or_create(name=keyword_name)
                    document.keywords.add(keyword)

            # Upload the file to S3
            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            s3 = session.client('s3')
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                document.s3_file_name,
                {'ContentType': file.content_type},
            )

        # Save the message if it is valid or create a placeholder if only a file was uploaded
        if form.is_valid() and form.cleaned_data.get('text'):
            print("Message form is valid.")
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            print("Message saved successfully.")
        elif document:  # Create a placeholder message if only a file is uploaded
            message = Message.objects.create(
                sender=request.user,
                conversation=conversation,
            )
            print("Placeholder message created for document.")

        # Link the document to the message, if applicable
        if message and document:
            message.document = document
            message.save()
            print("Document linked to the message.")

        return redirect('project_group', id=group.id)
    else:
        form = MessageForm()
        document_form = DocumentForm()

    return render(request, 'project_group.html', {
        'group': group,
        'conversation': conversation,
        'is_member': is_member,
        'is_owner': is_owner,
        'has_requested': has_requested,
        'document_form': document_form,
        'progress_percent': progress_percent,
        'form': form,
    })


def task_list(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_group = get_object_or_404(Project_group, id=id)

    tasks = Task.objects.filter(project_group=project_group)

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.project_group = project_group
            new_task.save()
            form.save_m2m()
            return redirect('tasks', id=id)
        else:
            return render(request, 'tasks.html', {'tasks': tasks, 'form': form, 'project_group': project_group, 'tried_submit': True})
    else:
        form = TaskForm()

    return render(request, 'tasks.html', {'tasks': tasks, 'project_group': project_group, 'form':form, 'tried_submit': False})

def mark_complete(request, task_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.is_complete = True
        task.save()
        return redirect('tasks', id=task.project_group.id)
    return

def delete_task(request, task_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks', id=task.project_group.id)
    return

@login_required
def conversation(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')

    conversation = get_object_or_404(Conversation, id=id)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        document_form = DocumentForm(request.POST, request.FILES)

        message = None
        document = None

        # Save the document if the form is valid and a file is provided
        if document_form.is_valid() and request.FILES.get('file'):
            file = request.FILES['file']
            file_name = document_form.cleaned_data.get('file_name', file.name)
            document = Document.objects.create(
                user=request.user,
                file_name=file_name,
                file_extension=file.name.split('.')[-1],
                description=document_form.cleaned_data.get('description', ''),
                s3_file_name=file.name,  # Replace with S3 handling if required
            )
            document.save()

            # Save keywords if provided
            keywords = document_form.cleaned_data.get('keywords', '')
            for keyword_name in keywords.split(','):
                keyword_name = keyword_name.strip()
                if keyword_name:
                    keyword, _ = Keyword.objects.get_or_create(name=keyword_name)
                    document.keywords.add(keyword)

            # Upload the file to S3
            session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            s3 = session.client('s3')
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                document.s3_file_name,
                {'ContentType': file.content_type},
            )

        # Save the message if it is valid or create a placeholder if only a file was uploaded
        if form.is_valid() and form.cleaned_data.get('text'):
            print("Message form is valid.")
            message = form.save(commit=False)
            message.sender = request.user
            message.conversation = conversation
            message.save()
            print("Message saved successfully.")
        elif document:  # Create a placeholder message if only a file is uploaded
            message = Message.objects.create(
                sender=request.user,
                conversation=conversation,
            )
            print("Placeholder message created for document.")

        # Link the document to the message, if applicable
        if message and document:
            message.document = document
            message.save()
            print("Document linked to the message.")

        return redirect('conversation', id=conversation.id)
    else:
        form = MessageForm()
        document_form = DocumentForm()

    return render(request, 'conversation.html', {
        'conversation': conversation,
        'form': form,
        'document_form': document_form,
    })

def join_conversation(request, conversation_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user.project_user not in conversation.participants.all():
        conversation.participants.add(request.user.project_user)
    
    return redirect('conversation', id=conversation_id)

def get_project_user_context(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    context = {
        'project_user': project_user,
    }
    return context

def get_project_user(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    if request.user.is_authenticated:
        try:
            project_user = Project_user.objects.get(user=request.user)
        except Project_user.DoesNotExist:
            print("project user not found in database")
            project_user = None
        return project_user
    print("user unauthenticated")
    return None

def create_conversation(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    if request.method == 'POST':
        form = CreateConversationForm(request.POST)
        if form.is_valid():
            conversation = Conversation.objects.create(is_DM=True)
            users = form.cleaned_data['users']
            conversation.participants.add(request.user.project_user) 
            for user in users:
                conversation.participants.add(user.project_user)
            conversation.save()
            return redirect('conversation', id=conversation.id)
    else:
        form = CreateConversationForm()
    return render(request, 'create_conversation.html', {'form': form})

def delete_conversation(request, conversation_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user.project_user in conversation.participants.all():
        conversation.participants.remove(request.user.project_user)
        if conversation.participants.count() == 0:
            conversation.delete()
    
    return redirect('common_user_dashboard')

def create_project(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    if project_user.role != 'COMMON':
        return redirect('home')  # Redirect if the user is not a common user

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project_group = form.save(commit=False)
            project_group.owner = project_user
            project_group.save()
            project_group.members.add(project_user)  # Add creator as a member
            project_group.save()
            # Create a default conversation for the project
            conversation = Conversation.objects.create(project_group=project_group)
            conversation.participants.add(project_user)
            conversation.save()
            return redirect('project_group', id=project_group.id)
    else:
        form = ProjectForm()

    return render(request, 'create_project.html', {'form': form})

def delete_project(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    project_group = get_object_or_404(Project_group, id=id)
    if project_group.owner != project_user:
        return redirect('project_group', id=id)

    # Delete associated documents from S3
    for document in project_group.documents.all():
        # Delete document from S3
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=document.s3_file_name)
        document.delete()

    # Delete the project group
    project_group.delete()
    return redirect('common_user_dashboard')

@login_required
def request_to_join_group(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    group = get_object_or_404(Project_group, id=id)

    # Check if the user is already a member
    if group.is_member(project_user):
        messages.info(request, "You are already a member of this group.")
        return redirect('project_group', id=id)

    # Check if the user has already requested to join
    if group.has_requested(project_user):
        messages.info(request, "You have already requested to join this group.")
        return redirect('project_group', id=id)

    # Create a join request
    JoinRequest.objects.create(user=project_user, group=group)
    messages.success(request, "Your request to join the group has been sent.")
    return redirect('project_group', id=id)

@login_required
def approve_join_request(request, request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    join_request = get_object_or_404(JoinRequest, id=request_id)
    group = join_request.group

    # Check if the current user is the owner of the group
    if group.owner != project_user:
        messages.error(request, "You are not authorized to approve this request.")
        return redirect('project_group', id=group.id)

    # Approve the request
    join_request.approved = True
    join_request.save()

    # Add the user to the group
    group.members.add(join_request.user)
    group.save()

    # Add the user to the group's conversation
    conversation = group.conversations.first()
    if conversation:
        conversation.participants.add(join_request.user)
        conversation.save()
    else:
        conversation = Conversation.objects.create(project_group=group)
        conversation.participants.add(join_request.user)
        conversation.save()

    messages.success(request, f"{join_request.user.username} has been added to the group.")
    return redirect('manage_join_requests', id=group.id)

@login_required
def reject_join_request(request, request_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    join_request = get_object_or_404(JoinRequest, id=request_id)
    group = join_request.group

    # Check if the current user is the owner of the group
    if group.owner != project_user:
        messages.error(request, "You are not authorized to reject this request.")
        return redirect('project_group', id=group.id)

    # Reject the request
    join_request.rejected = True
    join_request.save()

    messages.success(request, f"{join_request.user.username}'s request has been rejected.")
    return redirect('manage_join_requests', id=group.id)

@login_required
def manage_join_requests(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    group = get_object_or_404(Project_group, id=id)

    # Check if the current user is the owner of the group
    if group.owner != project_user:
        messages.error(request, "You are not authorized to manage join requests.")
        return redirect('project_group', id=group.id)

    join_requests = group.join_requests.filter(approved=False, rejected=False)

    return render(request, 'manage_join_requests.html', {
        'group': group,
        'join_requests': join_requests,
    })

@login_required
def leave_group(request, id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    project_user = get_project_user(request)
    group = get_object_or_404(Project_group, id=id)

    if not group.is_member(project_user):
        messages.error(request, "You are not a member of this group.")
        return redirect('project_group', id=id)

    if group.owner == project_user:
        messages.error(request, "Owners cannot leave their own group.")
        return redirect('project_group', id=id)

    remove_from_group(project_user, group)

    messages.success(request, "You have left the group.")
    return redirect('common_user_dashboard')

def remove_from_group(project_user, group):
    group.members.remove(project_user)
    group.save()

    #un-assign user from all tasks in the group 
    tasks = Task.objects.filter(project_group=group)
    for task in tasks.all():
        if project_user.user in task.assigned_users.all():
            task.assigned_users.remove(project_user.user)

    # Remove the user from the conversation
    conversation = group.conversations.first()
    if conversation:
        conversation.participants.remove(project_user)
        conversation.save()
    return


def search_documents_by_keyword(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access the dashboard.")
        return redirect('anon_dashboard')
    if request.user.is_superuser:
        return redirect('/admin/')
    
    query = request.GET.get('q', '').strip()  # Get the search keyword from the request
    results = []

    if query:
        results = query_documents(get_project_user(request), query)

    return render(request, 'search_results.html', {'query': query, 'results': results})

def query_documents(project_user, query):
    groups = project_user.project_groups.all()
    conversations = Conversation.objects.filter(participants=project_user)

    matching_keywords = Keyword.objects.filter(name__icontains=query)

    user_documents = Document.objects.filter(user=project_user.user, keywords__in=matching_keywords)
    group_documents = Document.objects.filter(project_group__in=groups, keywords__in=matching_keywords)
    message_documents = Document.objects.filter(message__conversation__in=conversations, keywords__in=matching_keywords)

    documents = (user_documents | group_documents | message_documents).distinct()

    return {'documents': documents}

@login_required
def user_profile(request):
    project_user = get_project_user(request)
    context = {
        'username': project_user.get_username(),
        'join_date': project_user.join_date,
        'email': project_user.email,
        'real_name': project_user.real_name,
    }
    return render(request, 'user_profile.html', context)