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
    TRIGGER_TYPES = [
        ('kafka_to_kafka', 'Kafka to Kafka Replay'),
        ('kafka_to_mq', 'Kafka to MQ Replay'),
        ('mq_to_mq', 'MQ to MQ Replay'),
        ('mq_to_kafka', 'MQ to Kafka Replay'),
        ('db_operation', 'DB Updates and Queries'),
    ]

    PERSITANT_INFRA = [
        ('kafka', 'Kafka'),
        ('mq', 'MQ'),
        ('cps', 'CPS'),
        ('database', 'DB'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, related_name='steps', on_delete=models.CASCADE)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_from = models.CharField(max_length=50, choices=PERSITANT_INFRA)
    trigger_to = models.CharField(max_length=50, choices=PERSITANT_INFRA)
    action_config = models.TextField()
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}: {self.get_trigger_type_display()}"