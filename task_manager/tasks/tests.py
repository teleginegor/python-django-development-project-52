from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.test import TestCase, Client
from django.urls import reverse_lazy

from task_manager import texts
from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.models import User


class TasksTest(TestCase):

    fixtures = ['tasks.json', 'labels.json', 'statuses.json', 'users.json']

    test_task = {
        'name': 'Task',
        'description': 'Task description',
        'status': 2,
        'executor': 2,
        'labels': [2, 3]
    }

    def setUp(self):
        self.task1 = Task.objects.get(pk=1)
        self.task2 = Task.objects.get(pk=2)
        self.task3 = Task.objects.get(pk=3)

        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.user3 = User.objects.get(pk=3)

        self.status1 = Status.objects.get(pk=1)
        self.status2 = Status.objects.get(pk=2)
        self.status3 = Status.objects.get(pk=3)

        self.label1 = Label.objects.get(pk=1)
        self.label2 = Label.objects.get(pk=2)
        self.label3 = Label.objects.get(pk=3)

        self.client: Client = Client()
        self.client.force_login(self.user1)

    def test_tasks(self):
        response = self.client.get(reverse_lazy('tasks'))
        tasks_list = list(response.context['tasks'])
        task1, task2, task3 = tasks_list

        self.assertTrue(len(tasks_list) == 3)
        self.assertEqual(task1.name, 'Build monument')
        self.assertEqual(task2.description, 'The best job in IT')
        self.assertEqual(task3.name, 'Go to the theatre')

    def test_tasks_list(self):
        response = self.client.get(reverse_lazy('tasks'))

        self.assertTemplateUsed(
            response,
            template_name='tasks/tasks.html'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse_lazy('task_create'))
        self.assertContains(response, self.task1.name)
        self.assertContains(response, self.task2.name)
        self.assertContains(response, self.task3.name)

    def test_tasks_filter_by_status(self):
        response = self.client.get(
            reverse_lazy('tasks'),
            {'status': self.status2.pk}
        )
        tasks = response.context['tasks']

        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_tasks_filter_by_executor(self):
        response = self.client.get(
            reverse_lazy('tasks'),
            {'executor': self.user2.pk}
        )
        tasks = response.context['tasks']

        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task2, tasks)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task1, tasks)

    def test_tasks_filter_by_label(self):
        response = self.client.get(
            reverse_lazy('tasks'),
            {'labels': self.label2.pk}
        )
        tasks = response.context['tasks']

        self.assertEqual(tasks.count(), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_tasks_filter_by_current_user(self):
        response = self.client.get(reverse_lazy('tasks'), {'personal': 'on'})
        tasks = response.context['tasks']

        self.assertEqual(tasks.count(), 1)
        self.assertIn(self.task3, tasks)
        self.assertNotIn(self.task1, tasks)
        self.assertNotIn(self.task2, tasks)

    def test_task_detai(self):
        response = self.client.get(
            reverse_lazy('task_detail', args=[self.task2.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            template_name='tasks/task_detail.html'
        )

    def test_task_create_get(self):
        response = self.client.get(reverse_lazy('task_create'))

        self.assertTemplateUsed(response, template_name='form.html')
        self.assertEqual(response.status_code, 200)

    def test_task_create_post(self):
        params = self.test_task
        params.update({'name': ''})
        response = self.client.post(reverse_lazy('task_create'), data=params)
        errors = response.context['form'].errors

        self.assertIn('name', errors)
        self.assertEqual(
            ['Обязательное поле.'],
            errors['name']
        )

        params.update({'name': 'Task'})
        response = self.client.post(reverse_lazy('task_create'), data=params)
        self.assertTrue(Task.objects.get(id=4))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('tasks'))

        params.update({'status': ''})
        response = self.client.post(reverse_lazy('task_create'), data=params)
        errors = response.context['form'].errors

        self.assertIn('status', errors)
        self.assertEqual(
            ['Обязательное поле.'],
            errors['status']
        )

    def test_task_update_get(self):
        response = self.client.get(
            reverse_lazy('task_update', args=[self.task1.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='form.html')

    def test_task_update_post(self):
        params = self.test_task
        params.update({'status': 2})
        response = self.client.post(
            reverse_lazy('task_update', args=[self.task1.id]),
            data=params
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('tasks'))

        updated_task = Task.objects.get(id=self.task1.id)
        self.assertEqual(updated_task.name, params['name'])
        self.assertEqual(updated_task.description, params['description'])

    def test_task_delete_get(self):
        response = self.client.get(
            reverse_lazy('task_delete', args=[self.task3.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='delete.html')

    def test_task_delete_post_author(self):
        before_objs_len = len(Task.objects.all())
        response = self.client.post(
            reverse_lazy('task_delete', args=[self.task3.id])
        )
        after_objs_len = len(Task.objects.all())

        self.assertTrue(after_objs_len == before_objs_len - 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('tasks'))
        with self.assertRaises(ObjectDoesNotExist):
            Task.objects.get(id=self.task3.id)

    def test_task_delete_post_not_author(self):
        before_objs_len = len(Task.objects.all())
        self.client.post(
            reverse_lazy('task_delete', args=[self.task1.id])
        )
        after_objs_len = len(Task.objects.all())

        self.assertTrue(after_objs_len == before_objs_len)
        self.assertRaisesMessage(
            expected_exception=PermissionDenied,
            expected_message=texts.messages['no_rights']
        )
