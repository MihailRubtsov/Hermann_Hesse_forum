from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Biography(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titel')
    content = models.TextField(verbose_name='Biografie-Text')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Geburtsdatum')
    image = models.ImageField(upload_to='bio_images/', null=True, blank=True, verbose_name='Foto')

    class Meta:
        verbose_name = 'Biografie'
        verbose_name_plural = 'Biografien'

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Genre-Name')

    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorien'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name='Titel')
    author = models.CharField(max_length=255, verbose_name='Autor')
    description = models.TextField(verbose_name='Beschreibung')
    image = models.ImageField(upload_to='books/', blank=True, null=True, verbose_name='Foto')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
        verbose_name='Kategorie',
    )

    class Meta:
        verbose_name = 'Buch'
        verbose_name_plural = 'Bücher'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'pk': self.pk})

    @property
    def average_rating(self):
        return self.reviews.aggregate(models.Avg('rating'))['rating__avg']


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews', verbose_name='Buch')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews',
                               verbose_name='Autor der Rezension')
    text = models.TextField(verbose_name='Rezensionstext')
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name='Bewertung',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rezension'
        verbose_name_plural = 'Rezensionen'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['book', 'author'], name='unique_review_per_user_and_book'),
        ]

    def __str__(self):
        return f'Rezension von {self.author} zu {self.book}'


class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Neu'),
        ('used', 'Gebraucht'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='listings', verbose_name='Buch')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name='Verkäufer')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preis')
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='used', verbose_name='Zustand')
    description = models.TextField(blank=True, verbose_name='Verkäuferkommentar')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Anzeige'
        verbose_name_plural = 'Anzeigen'
        ordering = ['price']

    def __str__(self):
        return f'{self.book} — {self.price} € ({self.seller})'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Profilbild')

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profile'

    def __str__(self):
        return f'Profil von {self.user.username}'


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages',
                               verbose_name='Absender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',
                                  verbose_name='Empfänger')
    text = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Gesendet am')
    is_read = models.BooleanField(default=False, verbose_name='Gelesen')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Nachricht'
        verbose_name_plural = 'Nachrichten'
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['sender', 'recipient']),
        ]

    def __str__(self):
        return f'Von {self.sender} an {self.recipient}'
