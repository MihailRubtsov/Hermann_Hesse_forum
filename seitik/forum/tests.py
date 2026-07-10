from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post, Thread


class ThreadDetailTests(TestCase):
    """Regressionstest: ein POST ohne 'submit_post' warf früher UnboundLocalError."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('autor', password='geheim12345')
        cls.thread = Thread.objects.create(title='Steppenwolf', creator=cls.user)
        Post.objects.create(thread=cls.thread, author=cls.user, content='Erster Beitrag')

    def test_post_without_submit_key_does_not_crash(self):
        self.client.login(username='autor', password='geheim12345')
        response = self.client.post(reverse('thread_detail', args=[self.thread.pk]), {})
        self.assertEqual(response.status_code, 200)

    def test_reply_creates_post(self):
        self.client.login(username='autor', password='geheim12345')
        self.client.post(reverse('thread_detail', args=[self.thread.pk]), {
            'submit_post': '1', 'content': 'Meine Antwort',
        })
        self.assertEqual(self.thread.posts.count(), 2)

    def test_empty_reply_is_rejected(self):
        self.client.login(username='autor', password='geheim12345')
        self.client.post(reverse('thread_detail', args=[self.thread.pk]), {
            'submit_post': '1', 'content': '   ',
        })
        self.assertEqual(self.thread.posts.count(), 1)


class CreateThreadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('autor', password='geheim12345')

    def test_creates_thread_with_first_post(self):
        self.client.login(username='autor', password='geheim12345')
        self.client.post(reverse('create_thread'), {
            'title': 'Demian', 'content': 'Was denkt ihr?',
        })
        thread = Thread.objects.get(title='Demian')
        self.assertEqual(thread.creator, self.user)
        self.assertEqual(thread.posts.count(), 1)

    def test_login_required(self):
        response = self.client.get(reverse('create_thread'))
        self.assertEqual(response.status_code, 302)


class DeletePostTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('besitzer', password='geheim12345')
        cls.stranger = User.objects.create_user('fremder', password='geheim12345')
        cls.thread = Thread.objects.create(title='Knulp', creator=cls.owner)
        cls.post = Post.objects.create(thread=cls.thread, author=cls.owner, content='Text')

    def test_stranger_cannot_delete(self):
        self.client.login(username='fremder', password='geheim12345')
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    def test_get_request_does_not_delete(self):
        self.client.login(username='besitzer', password='geheim12345')
        response = self.client.get(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 405)

    def test_owner_can_delete(self):
        self.client.login(username='besitzer', password='geheim12345')
        self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())
