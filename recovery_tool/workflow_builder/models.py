# recovery_tool/workflow_builder/models.py
from django.db import models
import uuid

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
    to_infra = models.CharField(max_length=50, choices=INFRA_TYPES)
    from_config = models.TextField()
    to_config = models.TextField()
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}: {self.event_type} from {self.from_infra} to {self.to_infra}"