from django.contrib import admin

from .models import Biography, Book, Category, Listing, Message, Profile, Review


@admin.register(Biography)
class BiographyAdmin(admin.ModelAdmin):
    list_display = ('title', 'birth_date')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'book_count')
    search_fields = ('name',)

    @admin.display(description='Bücher')
    def book_count(self, obj):
        return obj.books.count()


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'author', 'description')
    autocomplete_fields = ('category',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'author__username')
    raw_id_fields = ('book', 'author')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('book', 'seller', 'price', 'condition', 'created_at')
    list_filter = ('condition',)
    search_fields = ('book__title', 'seller__username')
    raw_id_fields = ('book', 'seller')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read',)
    raw_id_fields = ('sender', 'recipient')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    raw_id_fields = ('user',)
