# recovery_tool/workflow_builder/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Workflow, WorkflowStep, ActionLog
from .forms import WorkflowForm, WorkflowStepForm
import yaml
import json
import os
from django.utils import timezone
import uuid

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


# recovery_tool/workflow_builder/views.py
# Fixed execute_workflow view

@csrf_exempt
def execute_workflow(request, workflow_id):
    from .models import Workflow, WorkflowStep, WorkflowExecution, StepExecution
    
    workflow = get_object_or_404(Workflow, id=workflow_id)
    steps = workflow.steps.all().order_by('order')
    
    # Create a new execution record
    execution = WorkflowExecution.objects.create(
        workflow=workflow,
        status='pending'
    )
    
    # Create step execution records
    for i, step in enumerate(steps):
        StepExecution.objects.create(
            workflow_execution=execution,
            step=step,
            order=i,
            status='pending'
        )
    
    # Start execution in background (using simple threading for now)
    import threading
    
    def run_execution():
        try:
            execution.status = 'running'
            execution.started_at = timezone.now()
            execution.save(update_fields=['status', 'started_at'])
            
            # Execute each step in sequence
            for step_execution in execution.step_executions.all().order_by('order'):
                # Update step status
                step_execution.status = 'running'
                step_execution.started_at = timezone.now()
                step_execution.save(update_fields=['status', 'started_at'])
                
                try:
                    # Just a simple simulation for now
                    import time
                    time.sleep(2)  # Simulate processing time
                    
                    # Mark step as completed
                    step_execution.status = 'completed'
                    step_execution.completed_at = timezone.now()
                    step_execution.log_output = f"Simulated execution of {step_execution.step.event_type}"
                    step_execution.save(update_fields=['status', 'completed_at', 'log_output'])
                except Exception as e:
                    # Mark step as failed
                    step_execution.status = 'failed'
                    step_execution.completed_at = timezone.now()
                    step_execution.error_message = str(e)
                    step_execution.save(update_fields=['status', 'completed_at', 'error_message'])
                    
                    # Mark workflow as failed
                    execution.status = 'failed'
                    execution.completed_at = timezone.now()
                    execution.error_message = f"Failed at step {step_execution.order + 1}: {str(e)}"
                    execution.save(update_fields=['status', 'completed_at', 'error_message'])
                    return
            
            # All steps completed successfully
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save(update_fields=['status', 'completed_at'])
            
        except Exception as e:
            # Handle unexpected errors
            execution.status = 'failed'
            execution.completed_at = timezone.now()
            execution.error_message = str(e)
            execution.save(update_fields=['status', 'completed_at', 'error_message'])
    
    # Start the execution in a background thread
    thread = threading.Thread(target=run_execution)
    thread.daemon = True
    thread.start()
    
    return redirect('execution_status', execution_id=execution.id)

# recovery_tool/workflow_builder/views.py

def action_module(request):
    """Main page for the action module"""
    # Get recent action logs
    action_logs = ActionLog.objects.all().order_by('-created_at')[:10]
    
    return render(request, 'workflow_builder/action_module.html', {
        'action_logs': action_logs,
        'infra_types': WorkflowStep.INFRA_TYPES,
    })

def create_action(request):
    """Create and execute a new action"""
    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        source_type = request.POST.get('source_type')
        target_type = request.POST.get('target_type')
        source_config = request.POST.get('source_config', '')
        target_config = request.POST.get('target_config', '')
        
        # Parse parameters
        parameters = {}
        if request.POST.get('max_messages'):
            try:
                parameters['max_messages'] = int(request.POST.get('max_messages'))
            except ValueError:
                pass
                
        # Create action log
        action_log = ActionLog.objects.create(
            action_type=action_type,
            source_type=source_type,
            target_type=target_type,
            source_config=source_config,
            target_config=target_config,
            parameters=parameters,
            status='pending'
        )
        
        # Execute action in background
        from .action_handlers import execute_action_async
        execute_action_async(action_log.id)
        
        return redirect('action_status', action_id=action_log.id)
    
    # If not POST, redirect to action module page
    return redirect('action_module')

def action_status(request, action_id):
    """View the status of an action"""
    action_log = get_object_or_404(ActionLog, id=action_id)
    
    return render(request, 'workflow_builder/action_status.html', {
        'action_log': action_log
    })

def action_status_api(request, action_id):
    """API endpoint to get the current status of an action"""
    action_log = get_object_or_404(ActionLog, id=action_id)
    
    data = {
        'id': str(action_log.id),
        'action_type': action_log.action_type,
        'source_type': action_log.source_type,
        'target_type': action_log.target_type,
        'status': action_log.status,
        'created_at': action_log.created_at.isoformat(),
        'started_at': action_log.started_at.isoformat() if action_log.started_at else None,
        'completed_at': action_log.completed_at.isoformat() if action_log.completed_at else None,
        'result_summary': action_log.result_summary,
        'log_output': action_log.log_output,
        'error_message': action_log.error_message,
    }
    
    return JsonResponse(data)


def execution_status(request, execution_id):
    from .models import WorkflowExecution, StepExecution
    
    execution = get_object_or_404(WorkflowExecution, id=execution_id)
    step_executions = execution.step_executions.all().order_by('order')
    
    return render(request, 'workflow_builder/execution_status.html', {
        'execution': execution,
        'workflow': execution.workflow,
        'step_executions': step_executions,
    })

# recovery_tool/workflow_builder/views.py

def simulate_workflow(request, workflow_id):
    """
    Simulate a workflow execution without actually running anything on the backend.
    This is useful for UI testing and demonstrations.
    """
    workflow = get_object_or_404(Workflow, id=workflow_id)
    steps = workflow.steps.all().order_by('order')
    
    # Create dummy step data for the simulation
    simulated_steps = []
    for i, step in enumerate(steps):
        step_data = {
            'id': str(uuid.uuid4()),
            'order': i,
            'step': step,
            'step_type': step.event_type,
            'from_infra': step.from_infra,
            'to_infra': step.to_infra,
            'status': 'pending'
        }
        simulated_steps.append(step_data)
    
    return render(request, 'workflow_builder/simulate_workflow.html', {
        'workflow': workflow,
        'steps': simulated_steps,
        'start_time': timezone.now().isoformat()
    })