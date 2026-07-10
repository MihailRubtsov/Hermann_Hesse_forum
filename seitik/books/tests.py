from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from .models import Book, Category, Listing, Message, Review


class BookPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Roman')
        cls.book = Book.objects.create(
            title='Siddhartha',
            author='Hermann Hesse',
            description='Eine indische Dichtung.',
            category=cls.category,
        )

    def test_book_list_is_public(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Siddhartha')

    def test_search_filters_books(self):
        Book.objects.create(title='Demian', author='Hermann Hesse', description='Roman')
        response = self.client.get(reverse('book_list'), {'q': 'Siddhartha'})
        self.assertContains(response, 'Siddhartha')
        self.assertNotContains(response, 'Demian')

    def test_category_filter(self):
        other = Category.objects.create(name='Gedichte')
        Book.objects.create(title='Lyrik', author='H. H.', description='Verse', category=other)
        response = self.client.get(reverse('book_list'), {'category': self.category.id})
        self.assertContains(response, 'Siddhartha')
        self.assertNotContains(response, 'Lyrik')

    def test_anonymous_user_does_not_see_forms(self):
        response = self.client.get(self.book.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'submit_review')


class ReviewConstraintTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('leser', password='geheim12345')
        cls.book = Book.objects.create(title='Demian', author='H. H.', description='Roman')

    def test_only_one_review_per_user_and_book(self):
        Review.objects.create(book=self.book, author=self.user, text='Gut', rating=5)
        with self.assertRaises(IntegrityError):
            Review.objects.create(book=self.book, author=self.user, text='Nochmal', rating=4)

    def test_second_review_via_view_is_rejected(self):
        self.client.login(username='leser', password='geheim12345')
        Review.objects.create(book=self.book, author=self.user, text='Gut', rating=5)

        self.client.post(self.book.get_absolute_url(), {
            'submit_review': '1', 'text': 'Zweite', 'rating': 3,
        })
        self.assertEqual(self.book.reviews.count(), 1)

    def test_average_rating(self):
        other = User.objects.create_user('zweiter', password='geheim12345')
        Review.objects.create(book=self.book, author=self.user, text='a', rating=5)
        Review.objects.create(book=self.book, author=other, text='b', rating=3)
        self.assertEqual(self.book.average_rating, 4.0)


class InboxTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.me = User.objects.create_user('ich', password='geheim12345')
        cls.sender_only = User.objects.create_user('absender', password='geheim12345')
        cls.recipient_only = User.objects.create_user('empfaenger', password='geheim12345')

        # Jemand hat MIR geschrieben — ich habe nie geantwortet.
        Message.objects.create(sender=cls.sender_only, recipient=cls.me, text='Hallo')
        # ICH habe jemandem geschrieben.
        Message.objects.create(sender=cls.me, recipient=cls.recipient_only, text='Hallo zurueck')

    def test_inbox_shows_both_directions(self):
        self.client.login(username='ich', password='geheim12345')
        response = self.client.get(reverse('inbox'))
        self.assertContains(response, 'absender')
        self.assertContains(response, 'empfaenger')

    def test_opening_chat_marks_messages_as_read(self):
        self.client.login(username='ich', password='geheim12345')
        self.assertEqual(Message.objects.filter(recipient=self.me, is_read=False).count(), 1)

        self.client.get(reverse('chat', args=[self.sender_only.id]))
        self.assertEqual(Message.objects.filter(recipient=self.me, is_read=False).count(), 0)

    def test_cannot_chat_with_yourself(self):
        self.client.login(username='ich', password='geheim12345')
        response = self.client.get(reverse('chat', args=[self.me.id]))
        self.assertRedirects(response, reverse('inbox'))


class DeletionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('besitzer', password='geheim12345')
        cls.stranger = User.objects.create_user('fremder', password='geheim12345')
        cls.book = Book.objects.create(title='Knulp', author='H. H.', description='Erzaehlung')
        cls.listing = Listing.objects.create(book=cls.book, seller=cls.owner, price=10)

    def test_get_request_does_not_delete(self):
        self.client.login(username='besitzer', password='geheim12345')
        response = self.client.get(reverse('delete_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Listing.objects.filter(id=self.listing.id).exists())

    def test_stranger_cannot_delete(self):
        self.client.login(username='fremder', password='geheim12345')
        response = self.client.post(reverse('delete_listing', args=[self.listing.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Listing.objects.filter(id=self.listing.id).exists())

    def test_owner_can_delete(self):
        self.client.login(username='besitzer', password='geheim12345')
        self.client.post(reverse('delete_listing', args=[self.listing.id]))
        self.assertFalse(Listing.objects.filter(id=self.listing.id).exists())
