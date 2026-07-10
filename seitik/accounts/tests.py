from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignUpTests(TestCase):
    def test_signup_creates_user_with_email(self):
        self.client.post(reverse('signup'), {
            'username': 'neuling',
            'email': 'neuling@example.com',
            'password1': 'ein-sicheres-passwort-42',
            'password2': 'ein-sicheres-passwort-42',
        })
        user = User.objects.get(username='neuling')
        self.assertEqual(user.email, 'neuling@example.com')

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user('erster', email='taken@example.com', password='geheim12345')
        response = self.client.post(reverse('signup'), {
            'username': 'zweiter',
            'email': 'taken@example.com',
            'password1': 'ein-sicheres-passwort-42',
            'password2': 'ein-sicheres-passwort-42',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='zweiter').exists())


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user('leser', password='geheim12345')

    def test_login_redirects_to_book_list(self):
        response = self.client.post(reverse('login'), {
            'username': 'leser', 'password': 'geheim12345',
        })
        self.assertRedirects(response, reverse('book_list'))

    def test_protected_page_redirects_anonymous_user(self):
        response = self.client.get(reverse('profile'))
        self.assertIn(reverse('login'), response['Location'])
