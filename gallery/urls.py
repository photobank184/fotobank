from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),

    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),

    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('edit/<int:pk>/', views.PostUpdateView.as_view(), name='post_edit'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/<int:post_id>/<int:photo_id>/', views.contact_author, name='contact_author'),
    path('authors/', views.AuthorsListView.as_view(), name='authors_list'),
    path('author/<str:username>/', views.AuthorPostsView.as_view(), name='author_posts'),
]