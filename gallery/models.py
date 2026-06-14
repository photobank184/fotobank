from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile

from slugify import slugify
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO
import os
import math

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )

    cover = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='Обложка'
    )

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

    slug = models.SlugField(
        max_length=255,
        db_index=True,
        blank=True
    )

    description = models.TextField(blank=True)

    categories = models.ManyToManyField(
        Category,
        related_name='posts',
        blank=True,
        verbose_name='Категории'
    )

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def generate_unique_slug(self):
        base_slug = slugify(self.title)

        if not base_slug:
            base_slug = 'photo'

        slug = base_slug
        counter = 2

        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        if not self.slug:
            self.slug = self.generate_unique_slug()

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

    image = models.ImageField(
        upload_to='photos/',
        verbose_name='Оригинальное фото'
    )

    watermarked_image = models.ImageField(
        upload_to='photos/watermarked/',
        blank=True,
        null=True,
        verbose_name='Фото с водяным знаком'
    )

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

    class Meta:
        verbose_name = 'Фото'
        verbose_name_plural = 'Фотографии'
        ordering = ['-created_at']

    @property
    def is_free(self):
        return self.license_type == self.LICENSE_FREE

    def __str__(self):
        return self.title or f'{self.post.title} #{self.id}'

    def get_watermark_font(self, font_size):
        possible_fonts = [
            'arial.ttf',
            'Arial.ttf',
            'DejaVuSans.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ]

        for font_path in possible_fonts:
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception:
                continue

        return ImageFont.load_default()

    def make_watermark(self):
        if not self.image:
            return

        original = Image.open(self.image)
        original = original.convert('RGBA')

        width, height = original.size

        watermark_text = 'PhotoBank.online'

        font_size = max(32, width // 14)
        font = self.get_watermark_font(font_size)

        text_layer = Image.new('RGBA', original.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_layer)

        try:
            text_box = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_box[2] - text_box[0]
            text_height = text_box[3] - text_box[1]
        except Exception:
            text_width = font_size * len(watermark_text)
            text_height = font_size

        step_x = max(text_width + 140, width // 2)
        step_y = max(text_height + 160, height // 4)

        for y in range(-height, height * 2, step_y):
            for x in range(-width, width * 2, step_x):
                draw.text(
                    (x, y),
                    watermark_text,
                    font=font,
                    fill=(255, 255, 255, 95)
                )

        rotated_layer = text_layer.rotate(
            28,
            resample=Image.Resampling.BICUBIC,
            expand=False
        )

        watermarked = Image.alpha_composite(original, rotated_layer)
        watermarked = watermarked.convert('RGB')

        output = BytesIO()
        watermarked.save(output, format='JPEG', quality=90, optimize=True)
        output.seek(0)

        original_name = os.path.basename(self.image.name)
        name_without_ext, _ = os.path.splitext(original_name)

        filename = f'watermarked_{name_without_ext}.jpg'

        self.watermarked_image.save(
            filename,
            ContentFile(output.read()),
            save=False
        )

    def save(self, *args, **kwargs):
        old_image_name = None

        if self.pk:
            try:
                old_photo = Photo.objects.get(pk=self.pk)
                old_image_name = old_photo.image.name
            except Photo.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        image_changed = old_image_name != self.image.name

        if self.image and (not self.watermarked_image or image_changed):
            self.make_watermark()
            super().save(update_fields=['watermarked_image'])