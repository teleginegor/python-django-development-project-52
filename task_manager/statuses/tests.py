from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.test import TestCase, Client
from django.urls import reverse_lazy

from task_manager import texts
from task_manager.statuses.models import Status
from task_manager.users.models import User


class StatusesTest(TestCase):
    fixtures = ['statuses.json', 'users.json', 'tasks.json', 'labels.json']
    test_status = {
        'name': 'Test'
    }

    def setUp(self):
        self.status1 = Status.objects.get(pk=1)
        self.status2 = Status.objects.get(pk=2)
        self.status3 = Status.objects.get(pk=3)
        self.client = Client()
        self.client.force_login(User.objects.get(pk=1))

    def test_statuses(self):
        response = self.client.get(reverse_lazy('statuses'))
        statuses_list = list(response.context['statuses'])
        status1, status2, status3 = statuses_list

        self.assertTrue(len(statuses_list) == 3)
        self.assertEqual(status1.name, 'Start')
        self.assertEqual(status2.name, 'Process')
        self.assertEqual(status3.name, 'Finish')

    def test_statuses_list(self):
        response = self.client.get(reverse_lazy('statuses'))

        self.assertTemplateUsed(
            response,
            template_name='statuses/statuses.html'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse_lazy('create_status'))
        self.assertContains(response, self.status1.name)
        self.assertContains(response, self.status2.name)
        self.assertContains(response, self.status3.name)

    def test_status_create_get(self):
        response = self.client.get(reverse_lazy('create_status'))

        self.assertTemplateUsed(response, template_name='form.html')
        self.assertEqual(response.status_code, 200)

    def test_status_create_post(self):
        params = self.test_status
        params.update({'name': ''})
        response = self.client.post(reverse_lazy('create_status'), data=params)
        errors = response.context['form'].errors
        self.assertIn('name', errors)
        self.assertEqual(
            ['Обязательное поле.'],
            errors['name']
        )
        params.update({'name': 'Test'})
        response = self.client.post(reverse_lazy('create_status'), data=params)
        self.assertTrue(Status.objects.get(id=4))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('statuses'))

    def test_status_update_get(self):
        response = self.client.get(
            reverse_lazy('update_status', args=[self.status1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='form.html')

    def test_status_update_post(self):
        params = self.test_status
        response = self.client.post(
            reverse_lazy('update_status', args=[self.status1.id]),
            data=params
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('statuses'))

        updated_status = Status.objects.get(id=self.status1.id)
        self.assertEqual(updated_status.name, params['name'])

    def test_status_delete_get(self):
        response = self.client.get(
            reverse_lazy('delete_status', args=[self.status1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='delete.html')

    def test_status_delete_post(self):
        before_objs_len = len(Status.objects.all())
        response = self.client.post(
            reverse_lazy('delete_status', args=[self.status1.id])
        )
        after_objs_len = len(Status.objects.all())

        self.assertTrue(after_objs_len == before_objs_len - 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('statuses'))
        with self.assertRaises(ObjectDoesNotExist):
            Status.objects.get(id=self.status1.id)

    def test_status_delete_linked(self):
        before_objs_len = len(Status.objects.all())
        self.client.post(
            reverse_lazy('delete_status', args=[self.status2.id])
        )
        after_objs_len = len(Status.objects.all())
        self.assertTrue(after_objs_len == before_objs_len)
        self.assertRaisesMessage(
            expected_exception=ProtectedError,
            expected_message=texts.messages['protected_status']
        )
