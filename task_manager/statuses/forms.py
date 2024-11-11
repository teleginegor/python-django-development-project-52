from django import forms

from task_manager.statuses.models import Status
from task_manager.texts import create_status


class StatusForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150, required=True, label=create_status['status_name']
    )

    class Meta:
        model = Status
        fields = ('name',)
