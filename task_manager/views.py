from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import activate
from django.views.generic.base import TemplateView

from task_manager import texts


def set_language(request, language):
    activate(language)
    response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    response.set_cookie('django_language', language)
    return response


class BasicView(TemplateView):
    extra_context = {
        'basic': texts.basic,
        'texts': texts.index,
        'errors': texts.errors,
    }


class IndexView(BasicView):
    template_name = 'index.html'


class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'form.html'
    form_class = AuthenticationForm
    extra_context = {
        'basic': texts.basic,
        'login': texts.login,
        'title': texts.login['enter'],
        'button_text': texts.login['enter_text'],
    }
    next_page = reverse_lazy('home')
    success_message = texts.messages['logged']


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, texts.messages['logout'])
        return super().dispatch(request, *args, **kwargs)


class Error500View(BasicView):
    template_name = './errors/error_500.html'


class Error404View(BasicView):
    template_name = './errors/error_404.html'
