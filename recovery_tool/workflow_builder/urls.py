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
    path('about/', views.about, name='about'),
    path('documentation/', views.documentation, name='documentation'),
    path('actions/', views.action_module, name='action_module'),
    path('actions/create/', views.create_action, name='create_action'),
    path('actions/<uuid:action_id>/', views.action_status, name='action_status'),
    path('api/actions/<uuid:action_id>/status/', views.action_status_api, name='action_status_api'),
    path('execute/<uuid:workflow_id>/', views.execute_workflow, name='execute_workflow'),
    path('execution/<uuid:execution_id>/', views.execution_status, name='execution_status'),
    path('simulate/<uuid:workflow_id>/', views.simulate_workflow, name='simulate_workflow'),
]
