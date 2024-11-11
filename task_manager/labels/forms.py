from django import forms

from task_manager.labels.models import Label
from task_manager.texts import create_label


class LabelForm(forms.ModelForm):
    name = forms.CharField(
        max_length=150, required=True, label=create_label['label_name']
    )

    class Meta:
        model = Label
        fields = ('name',)
