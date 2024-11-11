from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from task_manager import texts
from task_manager.mixins import AuthCheckMixin, ProtectDeleteMixin
from task_manager.statuses.forms import StatusForm
from task_manager.statuses.models import Status


class StatusesListView(AuthCheckMixin, ListView):
    template_name = 'statuses/statuses.html'
    model = Status
    context_object_name = 'statuses'

    extra_context = {
        'basic': texts.basic,
        'texts': texts.create_status,
    }


class StatusCreateView(AuthCheckMixin, SuccessMessageMixin, CreateView):
    template_name = 'form.html'
    model = Status
    form_class = StatusForm

    success_url = reverse_lazy('statuses')
    success_message = texts.messages['status_created']

    extra_context = {
        'basic': texts.basic,
        'title': texts.create_status['status_create'],
        'button_text': texts.buttons['create_status']
    }


class StatusUpdateView(AuthCheckMixin, SuccessMessageMixin, UpdateView):
    template_name = 'form.html'
    model = Status
    form_class = StatusForm

    success_url = reverse_lazy('statuses')
    success_message = texts.messages['status_changed']

    extra_context = {
        'basic': texts.basic,
        'title': texts.create_status['status_change_title'],
        'button_text': texts.buttons['update_button']
    }


class StatusDeleteView(
    AuthCheckMixin,
    ProtectDeleteMixin,
    SuccessMessageMixin,
    DeleteView
):
    template_name = 'delete.html'
    model = Status

    success_url = reverse_lazy('statuses')
    success_message = texts.messages['status_deleted']

    protected_message = texts.messages['protected_status']
    protected_url = reverse_lazy('statuses')

    extra_context = {
        'basic': texts.basic,
        'title': texts.create_status['status_delete_title'],
        'delete_sure': texts.delete_user['delete_sure'],
        'dest_url': reverse_lazy('statuses'),
        'delete_cancel': texts.create_status['back_to_statuses'],
        'button_text': texts.buttons['delete_button']
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_obj'] = self.get_object().name
        return context
