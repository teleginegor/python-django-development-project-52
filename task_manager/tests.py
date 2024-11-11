from django.http import HttpRequest
from django.http.response import HttpResponseRedirect
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse_lazy

from task_manager import texts
from task_manager.users.models import User
from task_manager.views import set_language


class CustomTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            'username': 'test',
            'password': '123'
        }
        self.user = User.objects.create_user(**self.data)


class TestHome(CustomTestCase):
    def test_main_page(self):
        response = self.client.get(reverse_lazy('home'))

        self.assertTemplateUsed(response, template_name='index.html')
        self.assertContains(
            response,
            texts.basic['task_manager'],
            status_code=200
        )
        self.assertContains(response, reverse_lazy('users'))
        self.assertContains(response, reverse_lazy('create'))
        self.assertNotContains(response, reverse_lazy('logout'))

    def test_set_language(self):
        request = HttpRequest()
        request.META['HTTP_REFERER'] = reverse_lazy('home')
        response = set_language(request, 'en')

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertIn('django_language', response.cookies)
        self.assertEqual(response.cookies['django_language'].value, 'en')
        self.assertEqual(response.url, reverse_lazy('home'))


class TestLogin(CustomTestCase):
    def test_get_login(self):
        response = self.client.get(reverse_lazy('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='form.html')

    def test_post_login_sucsess(self):
        response = self.client.post(
            reverse_lazy('login'),
            self.data,
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse_lazy('home'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_post_login_error(self):
        self.data.update({'username': 'test1'})
        response = self.client.post(
            reverse_lazy('login'),
            self.data,
            follow=True
        )

        self.assertTemplateUsed(response, 'form.html')
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(response.context['user'].is_authenticated)


class TestLogoutUser(CustomTestCase):
    def test_user_logout(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse_lazy('logout'),
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse_lazy('home'))
        self.assertFalse(response.context['user'].is_authenticated)


class TestHeaderLogin(CustomTestCase):
    def test_header_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))

        self.assertContains(response, reverse_lazy('logout'))
        self.assertNotContains(response, reverse_lazy('login'))
