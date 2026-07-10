from django import forms

from .models import Book, Listing, Message, Profile, Review


INPUT = 'form-input'
FILE = 'form-file'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        labels = {
            'text': 'Ihre Eindrücke',
            'rating': 'Bewertung',
        }
        widgets = {
            'text': forms.Textarea(attrs={
                'class': INPUT,
                'rows': 4,
                'placeholder': 'Was hat Sie an diesem Buch bewegt?',
            }),
            'rating': forms.Select(attrs={'class': INPUT}),
        }


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['price', 'condition', 'description']
        labels = {
            'price': 'Preis (€)',
            'condition': 'Zustand',
            'description': 'Kommentar (optional)',
        }
        widgets = {
            'price': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01', 'min': '0'}),
            'condition': forms.Select(attrs={'class': INPUT}),
            'description': forms.Textarea(attrs={
                'class': INPUT,
                'rows': 2,
                'placeholder': 'Zustand des Einbands, Widmung, Auflage …',
            }),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Der Preis muss größer als 0 sein.')
        return price


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        labels = {'avatar': 'Profilbild'}
        widgets = {'avatar': forms.FileInput(attrs={'class': FILE, 'accept': 'image/*'})}


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        labels = {'text': 'Nachricht'}
        widgets = {
            'text': forms.Textarea(attrs={
                'class': INPUT,
                'rows': 2,
                'placeholder': 'Schreiben Sie eine Nachricht …',
            }),
        }

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if not text:
            raise forms.ValidationError('Die Nachricht darf nicht leer sein.')
        return text


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'image', 'category']
        labels = {
            'title': 'Titel',
            'author': 'Autor',
            'description': 'Beschreibung',
            'image': 'Bild',
            'category': 'Kategorie',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Titel eingeben'}),
            'author': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Autor des Buches'}),
            'description': forms.Textarea(attrs={'class': INPUT, 'rows': 4, 'placeholder': 'Buchbeschreibung'}),
            'category': forms.Select(attrs={'class': INPUT}),
            'image': forms.FileInput(attrs={'class': FILE, 'accept': 'image/*'}),
        }
