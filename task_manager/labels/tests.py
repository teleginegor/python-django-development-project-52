from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from django.test import TestCase, Client
from django.urls import reverse_lazy

from task_manager import texts
from task_manager.labels.models import Label
from task_manager.users.models import User


class LabelsTest(TestCase):
    fixtures = ['tasks.json', 'labels.json', 'statuses.json', 'users.json']
    test_label = {
        'name': 'For test'
    }

    def setUp(self):
        self.label1 = Label.objects.get(pk=1)
        self.label2 = Label.objects.get(pk=2)
        self.label3 = Label.objects.get(pk=3)
        self.client = Client()
        self.client.force_login(User.objects.get(pk=1))

    def test_labels(self):
        response = self.client.get(reverse_lazy('labels'))
        labels_list = list(response.context['labels'])
        label1, label2, label3 = labels_list

        self.assertTrue(len(labels_list) == 3)
        self.assertEqual(label1.name, 'Error')
        self.assertEqual(label2.name, 'Test')
        self.assertEqual(label3.name, 'Success')

    def test_labels_list(self):
        response = self.client.get(reverse_lazy('labels'))

        self.assertTemplateUsed(
            response,
            template_name='labels/labels.html'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse_lazy('create_label'))
        self.assertContains(response, self.label1.name)
        self.assertContains(response, self.label2.name)
        self.assertContains(response, self.label3.name)

    def test_label_create_get(self):
        response = self.client.get(reverse_lazy('create_label'))

        self.assertTemplateUsed(response, template_name='form.html')
        self.assertEqual(response.status_code, 200)

    def test_label_create_post(self):
        params = self.test_label
        params.update({'name': ''})
        response = self.client.post(reverse_lazy('create_label'), data=params)
        errors = response.context['form'].errors
        self.assertIn('name', errors)
        self.assertEqual(
            ['Обязательное поле.'],
            errors['name']
        )
        params.update({'name': 'For test'})
        response = self.client.post(reverse_lazy('create_label'), data=params)
        self.assertTrue(Label.objects.get(id=4))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('labels'))

    def test_label_update_get(self):
        response = self.client.get(
            reverse_lazy('update_label', args=[self.label1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='form.html')

    def test_label_update_post(self):
        params = self.test_label
        response = self.client.post(
            reverse_lazy('update_label', args=[self.label1.id]),
            data=params
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('labels'))

        updated_label = Label.objects.get(id=self.label1.id)
        self.assertEqual(updated_label.name, params['name'])

    def test_label_delete_get(self):
        response = self.client.get(
            reverse_lazy('delete_label', args=[self.label1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='delete.html')

    def test_label_delete_post(self):
        before_objs_len = len(Label.objects.all())
        response = self.client.post(
            reverse_lazy('delete_label', args=[self.label1.id])
        )
        after_objs_len = len(Label.objects.all())

        self.assertTrue(after_objs_len == before_objs_len - 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('labels'))
        with self.assertRaises(ObjectDoesNotExist):
            Label.objects.get(id=self.label1.id)

    def test_status_delete_linked(self):
        before_objs_len = len(Label.objects.all())
        self.client.post(
            reverse_lazy('delete_label', args=[self.label2.id])
        )
        after_objs_len = len(Label.objects.all())
        self.assertTrue(after_objs_len == before_objs_len)
        self.assertRaisesMessage(
            expected_exception=ProtectedError,
            expected_message=texts.messages['protected_label']
        )
