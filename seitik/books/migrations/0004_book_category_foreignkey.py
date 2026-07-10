"""Stellt Book.category wieder als ForeignKey her, ohne Daten zu verlieren.

In Migration 0002 war `category` ein ForeignKey, in 0003 wurde daraus ein
CharField. Diese Migration dreht das zurück und überträgt die vorhandenen
Textwerte in echte Category-Zeilen.
"""

import django.db.models.deletion
from django.db import migrations, models


def char_to_fk(apps, schema_editor):
    """Überträgt die Textwerte aus `category` in `category_fk`."""
    Book = apps.get_model('books', 'Book')
    Category = apps.get_model('books', 'Category')

    for book in Book.objects.exclude(category__isnull=True).exclude(category__exact=''):
        raw = book.category.strip()
        if not raw:
            continue

        # Falls in der Spalte noch alte Fremdschlüssel-IDs als Text stehen.
        if raw.isdigit() and Category.objects.filter(pk=int(raw)).exists():
            category = Category.objects.get(pk=int(raw))
        else:
            category, _ = Category.objects.get_or_create(name=raw)

        book.category_fk = category
        book.save(update_fields=['category_fk'])


def fk_to_char(apps, schema_editor):
    """Rückwärts: schreibt den Kategorienamen zurück in das Textfeld."""
    Book = apps.get_model('books', 'Book')
    for book in Book.objects.exclude(category_fk__isnull=True):
        book.category = book.category_fk.name
        book.save(update_fields=['category'])


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_biography_options_alter_book_options_and_more'),
    ]

    operations = [
        # Category.name muss eindeutig sein, damit get_or_create sauber arbeitet.
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Genre-Name'),
        ),
        migrations.AddField(
            model_name='book',
            name='category_fk',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='books',
                to='books.category',
                verbose_name='Kategorie',
            ),
        ),
        migrations.RunPython(char_to_fk, fk_to_char),
        migrations.RemoveField(model_name='book', name='category'),
        migrations.RenameField(model_name='book', old_name='category_fk', new_name='category'),
    ]
