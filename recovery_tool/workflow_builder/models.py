# recovery_tool/workflow_builder/models.py
from django.db import models
import uuid
from django.utils import timezone

class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    yaml_content = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class WorkflowStep(models.Model):
    EVENT_TYPES = [
        ('replay', 'Replay'),
        ('dump', 'Dump'),
        ('extract', 'Extract'),
        ('transform', 'Transform'),
        ('load', 'Load'),
        # Add new action types
        ('kafka_dump', 'Kafka Dump'),
        ('mq_dump', 'MQ Dump'),
    ]
    
    INFRA_TYPES = [
        ('kafka', 'Kafka'),
        ('mq', 'MQ'),
        ('db', 'Database'),
        ('servicebus', 'Service Bus'),
        ('file', 'File System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    from_infra = models.CharField(max_length=50, choices=INFRA_TYPES)
    to_infra = models.CharField(max_length=50, choices=INFRA_TYPES, null=True, blank=True)
    from_config = models.TextField()
    to_config = models.TextField(null=True, blank=True)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.event_type in ['kafka_dump', 'mq_dump']:
            return f"{self.workflow.name} - Step {self.order}: {self.get_event_type_display()} from {self.get_from_infra_display()}"
        elif self.to_infra:
            return f"{self.workflow.name} - Step {self.order}: {self.get_event_type_display()} from {self.get_from_infra_display()} to {self.get_to_infra_display()}"
        else:
            return f"{self.workflow.name} - Step {self.order}: {self.get_event_type_display()} from {self.get_from_infra_display()}"

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, related_name='executions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"Execution of {self.workflow.name} - {self.get_status_display()}"
    
    @property
    def duration(self):
        if self.completed_at:
            return self.completed_at - self.started_at
        elif self.status == 'running':
            return timezone.now() - self.started_at
        return None

class StepExecution(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_execution = models.ForeignKey(WorkflowExecution, related_name='step_executions', on_delete=models.CASCADE)
    step = models.ForeignKey(WorkflowStep, related_name='executions', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField()
    log_output = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Step {self.order} of {self.workflow_execution}"

class ActionLog(models.Model):
    """
    Model to track action results separate from workflow executions
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action_type = models.CharField(max_length=50)
    source_type = models.CharField(max_length=50, null=True, blank=True)
    target_type = models.CharField(max_length=50, null=True, blank=True)
    source_config = models.TextField(null=True, blank=True)
    target_config = models.TextField(null=True, blank=True)
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_summary = models.TextField(null=True, blank=True)
    log_output = models.TextField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None