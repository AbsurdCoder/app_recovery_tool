# recovery_tool/workflow_builder/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.workflow_list, name='workflow_list'),
    path('create/', views.create_workflow, name='create_workflow'),
    path('edit/<uuid:workflow_id>/', views.edit_workflow, name='edit_workflow'),
    path('view/<uuid:workflow_id>/', views.view_workflow, name='view_workflow'),
    path('save/<uuid:workflow_id>/', views.save_workflow, name='save_workflow'),
    path('execute/<uuid:workflow_id>/', views.execute_workflow, name='execute_workflow'),
]