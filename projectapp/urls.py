from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.common_user_dashboard, name='common_user_dashboard'),

    path('admin-dashboard/', views.pma_admin_dashboard, name='pma_admin_dashboard'),
    path('admin_dashboard/project/<int:project_id>/', views.pma_admin_project_detail, name='pma_admin_project_detail'),
    path('admin_dashboard/project/<int:project_id>/delete/', views.pma_admin_delete_project, name='pma_admin_delete_project'),
    path('admin_dashboard/file/<int:file_id>/delete/', views.pma_admin_delete_file, name='pma_admin_delete_file'),
    path('anon-dashboard/', views.anon_dashboard, name='anon_dashboard'),
    path('admin/', admin.site.urls),
    #path('dashboard/upload/', views.upload_file, name='upload_file'),
    #path('dashboard/files/', views.uploaded_files, name='uploaded_files'),
    path('dashboard/files/delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('create_project/', views.create_project, name='create_project'),
    path('groups/<int:id>/', views.project_group, name='project_group'),
    path('groups/<int:id>/tasks/', views.task_list, name='tasks'),
    path('tasks/mark_complete/<int:task_id>/', views.mark_complete, name='mark_complete'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('delete_project/<int:id>/', views.delete_project, name='delete_project'),
    path('conversations/<int:id>/', views.conversation, name='conversation'),
    path('conversation/create/', views.create_conversation, name='create_conversation'),
    path('conversation/<int:conversation_id>/join/', views.join_conversation, name='join_conversation'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('search/', views.search_documents_by_keyword, name='search_documents_by_keyword'),
    path('request_to_join_group/<int:id>/', views.request_to_join_group, name='request_to_join_group'),
    path('approve_join_request/<int:request_id>/', views.approve_join_request, name='approve_join_request'),
    path('reject_join_request/<int:request_id>/', views.reject_join_request, name='reject_join_request'),
    path('manage_join_requests/<int:id>/', views.manage_join_requests, name='manage_join_requests'),
    path('leave_group/<int:id>/', views.leave_group, name='leave_group'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('profile/', views.user_profile, name='user_profile'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
