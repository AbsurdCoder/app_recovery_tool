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
        fields = ['event_type', 'from_infra', 'to_infra', 'from_config', 'to_config']
        widgets = {
            'from_config': forms.Textarea(attrs={'rows': 4}),
            'to_config': forms.Textarea(attrs={'rows': 4}),
        }