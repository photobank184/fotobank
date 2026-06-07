from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    cover = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Обложка')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='authors/avatars/',
        blank=True,
        null=True
    )
    cover = models.ImageField(
        upload_to='authors/covers/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        blank=True,
        default='Фотограф PhotoBank'
    )
    location = models.CharField(
        max_length=120,
        blank=True
    )
    followers_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Профиль {self.user.username}'


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    categories = models.ManyToManyField(
        Category,
        related_name='posts',
        blank=True,
        verbose_name='Категории'
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class Photo(models.Model):
    LICENSE_FREE = 'free'
    LICENSE_RESTRICTED = 'restricted'

    LICENSE_CHOICES = [
        (LICENSE_FREE, 'Бесплатно для любых целей'),
        (LICENSE_RESTRICTED, 'Права ограничены автором'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    image = models.ImageField(upload_to='photos/')

    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название фото'
    )

    short_description = models.TextField(
        blank=True,
        verbose_name='Краткое описание'
    )

    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_CHOICES,
        default=LICENSE_FREE,
        verbose_name='Права использования'
    )

    price_note = models.CharField(
        max_length=100,
        blank=True,
        help_text='Напр.: 500₽ / Договорная'
    )

    camera_model = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фотоаппарат'
    )

    file_format = models.CharField(
        max_length=20,
        blank=True,
        default='JPG',
        verbose_name='Формат'
    )

    resolution = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Разрешение'
    )

    created_at = models.DateTimeField(default=timezone.now)

    @property
    def is_free(self):
        return self.license_type == self.LICENSE_FREE

    def __str__(self):
        return self.title or f"{self.post.title} #{self.id}"