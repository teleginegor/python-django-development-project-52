from django import forms
from django_filters import FilterSet, ModelChoiceFilter, BooleanFilter

from task_manager import texts
from task_manager.labels.models import Label
from task_manager.tasks.models import Task


class TaskFilter(FilterSet):
    labels = ModelChoiceFilter(
        queryset=Label.objects.all(),
        label=texts.create_tasks['task_label']
    )

    personal = BooleanFilter(
        widget=forms.CheckboxInput,
        method='get_personal',
        label=texts.create_tasks['personal_tasks']
    )

    def get_personal(self, queryset, _, value):
        if value:
            user = self.request.user
            return queryset.filter(author=user)
        return queryset

    class Meta:
        model = Task
        fields = ['status', 'executor']
