from django.urls import path
from .views import WorkSpaceCreateView, task_detail, \
    ws_list, delete_workspace, ws_update, search_account, add_member_to_ws, ws_detail, remove_ws_member

urlpatterns = [
    path('new-workspace/', WorkSpaceCreateView.as_view(), name='create-workspace'),
    path('workspaces/', ws_list, name='workspaces'),
    path('workspaces/<int:pk>/delete', delete_workspace, name='delete-workspace'),
    path('workspaces/<int:pk>/update', ws_update, name='update-workspace'),
    path('search-add-user/<slug:ws_slug>', search_account, name='search-account'),
    path('add-member-to-ws/<slug:ws_slug>', add_member_to_ws, name='add-member-to-ws'),

    path('workspaces/<slug:ws_slug>', ws_detail, name='workspace-detail'),
    path('workspaces/<slug:ws_slug>/<slug:task_slug>', task_detail, name='task-detail'),
    path('workspaces/<slug:ws_slug>/remove-member/<int:pk>/', remove_ws_member, name='remove-member'),
]
