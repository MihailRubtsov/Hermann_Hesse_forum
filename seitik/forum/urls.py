from django.urls import path

from . import views

urlpatterns = [
    path('forum/', views.all_threads, name='forum'),
    path('forum/create/', views.create_thread, name='create_thread'),
    path('thread/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
