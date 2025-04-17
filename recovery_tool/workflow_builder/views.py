# recovery_tool/workflow_builder/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Workflow, WorkflowStep
from .forms import WorkflowForm, WorkflowStepForm
import yaml
import json
import os

def workflow_list(request):
    workflows = Workflow.objects.all().order_by('-created_at')
    return render(request, 'workflow_builder/workflow_list.html', {'workflows': workflows})

def create_workflow(request):
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save()
            return redirect('edit_workflow', workflow_id=workflow.id)
    else:
        form = WorkflowForm()
    return render(request, 'workflow_builder/create_workflow.html', {'form': form})

def edit_workflow(request, workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    steps = workflow.steps.all().order_by('order')
    
    return render(request, 'workflow_builder/edit_workflow.html', {
        'workflow': workflow,
        'steps': steps,
        'event_types': WorkflowStep.EVENT_TYPES,
        'infra_types': WorkflowStep.INFRA_TYPES
    })

def about(request):
    """
    Render the About Us page.
    """
    return render(request, 'workflow_builder/about.html')

def documentation(request):
    """
    Render the Documentation page.
    """
    return render(request, 'workflow_builder/documentation.html')

@csrf_exempt
def save_workflow(request, workflow_id):
    if request.method == 'POST':
        workflow = get_object_or_404(Workflow, id=workflow_id)
        data = json.loads(request.body)
        
        # Delete existing steps
        workflow.steps.all().delete()
        
        # Add new steps
        for i, step_data in enumerate(data['steps']):
            WorkflowStep.objects.create(
                workflow=workflow,
                event_type=step_data['event_type'],
                from_infra=step_data['from_infra'],
                to_infra=step_data['to_infra'],
                from_config=step_data['from_config'],
                to_config=step_data['to_config'],
                order=i
            )
        
        # Generate YAML
        yaml_content = generate_yaml(workflow)
        workflow.yaml_content = yaml_content
        workflow.save()
        
        # Save YAML to file
        file_path = os.path.join(settings.WORKFLOW_YAML_DIR, f"{workflow.id}.yaml")
        with open(file_path, 'w') as f:
            f.write(yaml_content)
        
        return JsonResponse({'status': 'success', 'yaml': yaml_content})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def generate_yaml(workflow):
    workflow_dict = {
        'workflow': {
            'name': workflow.name,
            'description': workflow.description,
            'steps': []
        }
    }
    
    for step in workflow.steps.all().order_by('order'):
        step_dict = {
            'event_type': step.event_type,
            'from_infra': step.from_infra,
            'to_infra': step.to_infra,
            'from_config': step.from_config,
            'to_config': step.to_config
        }
        workflow_dict['workflow']['steps'].append(step_dict)
    
    return yaml.dump(workflow_dict, default_flow_style=False)

def view_workflow(request, workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    steps = workflow.steps.all().order_by('order')
    
    return render(request, 'workflow_builder/view_workflow.html', {
        'workflow': workflow,
        'steps': steps,
        'yaml_content': workflow.yaml_content
    })

def execute_workflow(request, workflow_id):
    workflow = get_object_or_404(Workflow, id=workflow_id)
    
    # Here you would implement logic to execute the workflow
    # For now, we'll just show that the workflow is being executed
    
    return render(request, 'workflow_builder/execution_result.html', {
        'workflow': workflow,
        'result': "Workflow execution started successfully."
    })