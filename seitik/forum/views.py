from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm, ThreadForm
from .models import Post, Thread

THREADS_PER_PAGE = 15


@login_required
def all_threads(request):
    threads = (
        Thread.objects
        .select_related('creator')
        .annotate(post_count=Count('posts'), last_activity=Max('posts__created_at'))
        .order_by('-created_at')
    )
    paginator = Paginator(threads, THREADS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'forum/forum.html', {
        'page_obj': page,
        'threads': page.object_list,
    })


@login_required
def thread_detail(request, pk):
    thread = get_object_or_404(Thread.objects.select_related('creator'), pk=pk)
    posts = thread.posts.select_related('author')

    post_form = PostForm()
    if request.method == 'POST' and 'submit_post' in request.POST:
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            return redirect('thread_detail', pk=pk)

    return render(request, 'forum/thread_detail.html', {
        'thread': thread,
        'posts': posts,
        'post_form': post_form,
    })


@login_required
def create_thread(request):
    if request.method == 'POST':
        thread_form = ThreadForm(request.POST)
        post_form = PostForm(request.POST)

        if thread_form.is_valid() and post_form.is_valid():
            thread = thread_form.save(commit=False)
            thread.creator = request.user
            thread.save()

            post = post_form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()

            messages.success(request, 'Ihr Thema wurde veröffentlicht.')
            return redirect('thread_detail', pk=thread.pk)
    else:
        thread_form = ThreadForm()
        post_form = PostForm()

    return render(request, 'forum/create_thread.html', {
        'thread_form': thread_form,
        'post_form': post_form,
    })


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    thread_id = post.thread_id
    post.delete()
    messages.success(request, 'Beitrag gelöscht.')
    return redirect('thread_detail', pk=thread_id)
