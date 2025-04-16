# recovery_tool/workflow_builder/forms.py
from django import forms
from .models import Workflow, WorkflowStep

class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['name', 'description']

class WorkflowStepForm(forms.ModelForm):
    class Meta:
        model = WorkflowStep
        fields = ['trigger_type', 'action_config']
        widgets = {
            'action_config': forms.Textarea(attrs={'rows': 4}),
        }