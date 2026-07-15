from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:recipient_id>/', views.chat_view, name='chat'),
    path('listing/<int:listing_id>/delete/', views.delete_listing, name='delete_listing'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('all_quotes', views.all_quotes, name='all_quotes'),
    path('create_quote', views.write_quote, name='create_quote')
]
