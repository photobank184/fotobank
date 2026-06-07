from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Count, Q

from .models import Post, Photo
from .forms import PostForm, PhotoFormSet, ContactForm

User = get_user_model()


class PostListView(ListView):
    model = Post
    template_name = 'gallery/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.filter(
            is_published=True
        ).select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'photos',
            'categories'
        )

        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(author__username__icontains=query)
            )

        return queryset.distinct().order_by('-published_at', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        authors = User.objects.filter(
            posts__is_published=True
        ).select_related(
            'profile'
        ).annotate(
            posts_count=Count('posts', filter=Q(posts__is_published=True))
        ).filter(
            posts_count__gt=0
        ).order_by('-posts_count')[:6]

        context['authors'] = authors

        return context

class AuthorPostsView(ListView):
    model = Post
    template_name = 'gallery/author_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        return Post.objects.filter(
            author=self.author,
            is_published=True
        ).select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'photos',
            'categories'
        ).order_by('-published_at', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = 'gallery/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'photos'
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['contact_form'] = ContactForm()

        category_ids = self.object.categories.values_list('id', flat=True)

        related_posts = Post.objects.filter(
            is_published=True,
            categories__in=category_ids
        ).exclude(
            id=self.object.id
        ).select_related(
            'author',
            'author__profile'
        ).prefetch_related(
            'photos',
            'categories'
        ).distinct().order_by('-published_at', '-created_at')[:10]

        ctx['related_posts'] = related_posts
        return ctx


class AuthorRequiredMixin(LoginRequiredMixin):
    pass


class PostCreateView(AuthorRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'gallery/post_form.html'
    success_url = reverse_lazy('gallery:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['formset'] = kwargs.get('formset') or PhotoFormSet(
            self.request.POST or None,
            self.request.FILES or None
        )
        return ctx

    def form_valid(self, form):
        form.instance.author = self.request.user
        ctx = self.get_context_data()
        formset = ctx['formset']

        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response

        return self.form_invalid(form)


class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'gallery/post_form.html'
    success_url = reverse_lazy('gallery:dashboard')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['formset'] = kwargs.get('formset') or PhotoFormSet(
            self.request.POST or None,
            self.request.FILES or None,
            instance=self.object
        )
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx['formset']

        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response

        return self.form_invalid(form)


def dashboard(request):
    posts = Post.objects.filter(
        author=request.user
    ).prefetch_related(
        'photos'
    ).order_by('-created_at')

    return render(request, 'gallery/dashboard.html', {'posts': posts})


def contact_author(request, post_id, photo_id):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid() and not form.cleaned_data.get('phone'):
            photo = get_object_or_404(Photo, id=photo_id, post_id=post_id)

            send_mail(
                subject=f'Запрос по фото: {photo.post.title}',
                message=(
                    f"От: {form.cleaned_data['name']} "
                    f"({form.cleaned_data['email']})\n\n"
                    f"Сообщение:\n{form.cleaned_data['message']}\n\n"
                    f"Ссылка: {request.build_absolute_uri()}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[photo.post.author.email],
                fail_silently=False,
            )

            messages.success(request, '✅ Запрос успешно отправлен автору!')
            return redirect('gallery:post_detail', pk=post_id)

        messages.error(request, '❌ Ошибка отправки или обнаружен спам.')

    return redirect('gallery:post_detail', pk=post_id)