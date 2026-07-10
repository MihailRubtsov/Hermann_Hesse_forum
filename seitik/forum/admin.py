from django.contrib import admin

from .models import Post, Thread


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    raw_id_fields = ('author',)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    search_fields = ('title', 'creator__username')
    raw_id_fields = ('creator',)
    inlines = [PostInline]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('thread', 'author', 'created_at')
    search_fields = ('content', 'author__username')
    raw_id_fields = ('thread', 'author')
