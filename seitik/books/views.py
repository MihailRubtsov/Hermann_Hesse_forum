from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import QuoteForm
from forum.models import Thread

from .forms import ListingForm, MessageForm, ProfileForm, ReviewForm
from .models import Biography, Book, Category, Listing, Message, Profile, Review, Quote

BOOKS_PER_PAGE = 9


def index(request):
    bio = Biography.objects.first()
    return render(request, 'books/biography.html', {'bio': bio})


def book_list(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    books = (
        Book.objects
        .select_related('category')
        .annotate(review_count=Count('reviews'))
        .order_by('title')
    )

    if query:
        books = books.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id.isdigit():
        books = books.filter(category_id=int(category_id))

    paginator = Paginator(books, BOOKS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'books/book_list.html', {
        'page_obj': page,
        'books': page.object_list,
        'total_count': paginator.count,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
    })


def book_detail(request, pk):
    book = get_object_or_404(Book.objects.select_related('category'), pk=pk)
    reviews = book.reviews.select_related('author')
    listings = book.listings.select_related('seller')

    has_reviewed = (
        request.user.is_authenticated
        and reviews.filter(author=request.user).exists()
    )

    review_form = ReviewForm()
    listing_form = ListingForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        # Rezension abschicken
        if 'submit_review' in request.POST:
            if has_reviewed:
                django_messages.error(request, 'Sie haben dieses Buch bereits rezensiert.')
                return redirect('book_detail', pk=pk)

            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.book = book
                review.author = request.user
                review.save()
                django_messages.success(request, 'Vielen Dank! Ihre Rezension wurde veröffentlicht.')
                return redirect('book_detail', pk=pk)

        elif 'submit_listing' in request.POST:
            listing_form = ListingForm(request.POST)
            if listing_form.is_valid():
                listing = listing_form.save(commit=False)
                listing.book = book
                listing.seller = request.user
                listing.save()
                django_messages.success(request, 'Ihre Anzeige ist jetzt online.')
                return redirect('book_detail', pk=pk)

    return render(request, 'books/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'listings': listings,
        'review_form': review_form,
        'listing_form': listing_form,
        'has_reviewed': has_reviewed,
    })


@login_required
def chat_view(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    if recipient == request.user:
        django_messages.error(request, 'Sie können sich nicht selbst schreiben.')
        return redirect('inbox')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.recipient = recipient
            msg.save()
            return redirect('chat', recipient_id=recipient_id)
    else:
        form = MessageForm()

    conversation = Message.objects.filter(
        Q(sender=request.user, recipient=recipient)
        | Q(sender=recipient, recipient=request.user)
    ).select_related('sender')

    Message.objects.filter(sender=recipient, recipient=request.user, is_read=False).update(is_read=True)

    return render(request, 'books/chat.html', {
        'recipient': recipient,
        'chat_messages': conversation,
        'form': form,
    })


@login_required
def inbox(request):
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).select_related('sender', 'recipient')

    partners = {}
    for msg in conversations:
        partner = msg.recipient if msg.sender == request.user else msg.sender
        entry = partners.setdefault(partner.id, {'user': partner, 'last': msg.created_at, 'unread': 0})
        entry['last'] = max(entry['last'], msg.created_at)
        if msg.recipient == request.user and not msg.is_read:
            entry['unread'] += 1

    contacts = sorted(partners.values(), key=lambda item: item['last'], reverse=True)
    return render(request, 'books/inbox.html', {'contacts': contacts})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Profilbild aktualisiert.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
        'listings': Listing.objects.filter(seller=request.user).select_related('book'),
        'reviews': Review.objects.filter(author=request.user).select_related('book'),
        'threads': Thread.objects.filter(creator=request.user).annotate(post_count=Count('posts')),
    }
    return render(request, 'books/profile.html', context)


@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, author=request.user)
    review.delete()
    django_messages.success(request, 'Rezension gelöscht.')
    return redirect('profile')


@login_required
@require_POST
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, seller=request.user)
    listing.delete()
    django_messages.success(request, 'Anzeige gelöscht.')
    return redirect('profile')

quotes_per_page = 15

@login_required
def all_quotes(request):
    quotes_list = Quote.objects.all().order_by('-created_at')
    paginator = Paginator(quotes_list, quotes_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'books/all_quotes.html', {
        'page_obj': page_obj,
    })



@login_required
def write_quote(request):
    if request.method == 'POST':
        quote_form = QuoteForm(request.POST)
        if quote_form.is_valid():
            quote = quote_form.save(commit=False)
            quote.creator = request.user
            quote.save()
            messages.success(request, 'Ihr Zitat wurde erfolgreich veröffentlicht.')
            return redirect('all_quotes')
    else:
        quote_form = QuoteForm()
    return render(request, 'books/create_quote.html',{'quote_form': quote_form})
        
        