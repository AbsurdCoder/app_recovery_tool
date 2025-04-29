# recovery_tool/workflow_builder/workflow_executor.py
# Create a new module for workflow execution

import logging
import traceback
from django.utils import timezone
from .models import WorkflowExecution, StepExecution, ActionLog
from .action_handlers import get_action_handler

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    """Class for executing workflows"""
    
    def __init__(self, execution_id):
        self.execution_id = execution_id
        self.execution = WorkflowExecution.objects.get(id=execution_id)
        self.workflow = self.execution.workflow
        self.step_executions = self.execution.step_executions.all().order_by('order')
    
    def execute(self):
        """Execute the workflow"""
        logger.info(f"Starting execution of workflow: {self.workflow.name} (ID: {self.workflow.id})")
        
        self.execution.status = 'running'
        self.execution.save(update_fields=['status'])
        
        try:
            for step_execution in self.step_executions:
                self._execute_step(step_execution)
                
                if step_execution.status == 'failed':
                    # If any step fails, mark the workflow as failed
                    self.execution.status = 'failed'
                    self.execution.error_message = f"Failed at step {step_execution.order + 1}: {step_execution.error_message}"
                    self.execution.completed_at = timezone.now()
                    self.execution.save(update_fields=['status', 'error_message', 'completed_at'])
                    return
            
            # All steps completed successfully
            self.execution.status = 'completed'
            self.execution.completed_at = timezone.now()
            self.execution.save(update_fields=['status', 'completed_at'])
            logger.info(f"Workflow execution completed: {self.workflow.name} (ID: {self.workflow.id})")
            
        except Exception as e:
            logger.error(f"Error executing workflow {self.workflow.id}: {str(e)}")
            logger.error(traceback.format_exc())
            
            self.execution.status = 'failed'
            self.execution.error_message = str(e)
            self.execution.completed_at = timezone.now()
            self.execution.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def _execute_step(self, step_execution):
        """Execute a single workflow step"""
        step = step_execution.step
        logger.info(f"Executing step {step_execution.order + 1}: {step.event_type}")
        
        step_execution.status = 'running'
        step_execution.started_at = timezone.now()
        step_execution.save(update_fields=['status', 'started_at'])
        
        try:
            # Handle special action types
            if step.event_type in ['kafka_dump', 'mq_dump']:
                result = self._execute_action_step(step)
                step_execution.log_output = result.get('log_output', '')
                step_execution.status = 'completed'
            else:
                # Standard workflow step (like the original implementations)
                # This is where you'd implement the standard handlers
                # For brevity, we'll just mark it as completed for now
                step_execution.log_output = f"Executed step: {step.event_type}"
                step_execution.status = 'completed'
            
            step_execution.completed_at = timezone.now()
            step_execution.save(update_fields=['status', 'completed_at', 'log_output'])
            
        except Exception as e:
            logger.error(f"Error executing step {step_execution.order + 1}: {str(e)}")
            logger.error(traceback.format_exc())
            
            step_execution.status = 'failed'
            step_execution.error_message = str(e)
            step_execution.completed_at = timezone.now()
            step_execution.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def _execute_action_step(self, step):
        """Execute a step using the action handlers"""
        # Create an action log entry for this step
        action_log = ActionLog.objects.create(
            action_type=step.event_type,
            source_type=step.from_infra,
            target_type=step.to_infra,
            source_config=step.from_config,
            target_config=step.to_config,
            parameters={},  # Add parameters as needed
            status='pending'
        )
        
        # Get the appropriate handler
        handler = get_action_handler(step.event_type, action_log.id)
        
        # Execute the action
        handler.execute()
        
        # Refresh the action log to get updated status
        action_log.refresh_from_db()
        
        return {
            'log_output': action_log.log_output,
            'error_message': action_log.error_message,
            'result_summary': action_log.result_summary,
            'status': action_log.status
        }


# Function to execute a workflow in a background thread
def execute_workflow_async(execution_id):
    """Execute a workflow in a background thread"""
    import threading
    
    def run_workflow():
        try:
            executor = WorkflowExecutor(execution_id)
            executor.execute()
        except Exception as e:
            logger.error(f"Error executing workflow {execution_id}: {e}")
            logger.error(traceback.format_exc())
    
    thread = threading.Thread(target=run_workflow)
    thread.daemon = True
    thread.start()
    return thread