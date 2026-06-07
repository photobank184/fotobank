from django.contrib import admin
from .models import Post, Photo, Profile, Category


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'location',
        'followers_count',
        'likes_count',
        'views_count',
    )

    search_fields = (
        'user__username',
        'user__email',
        'location',
        'bio',
    )


class PhotoInline(admin.StackedInline):
    model = Photo
    extra = 1

    fieldsets = (
        ('Изображение', {
            'fields': (
                'image',
                'title',
                'short_description',
            )
        }),

        ('Права использования', {
            'fields': (
                'license_type',
                'price_note',
            )
        }),

        ('Техническая информация', {
            'fields': (
                'camera_model',
                'file_format',
                'resolution',
            )
        }),

        ('Служебное', {
            'fields': (
                'created_at',
            )
        }),
    )

    readonly_fields = (

    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_published',
        'published_at',
        'created_at',
        'photos_count',
    )

    list_filter = (
        'is_published',
        'published_at',
        'created_at',
        'author',
    )

    search_fields = (
        'title',
        'description',
        'author__username',
        'author__email',
    )

    list_editable = (
        'is_published',
    )

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'author',
                'title',
                'description',
                'categories',
            )
        }),

        ('Публикация', {
            'fields': (
                'is_published',
                'published_at',
                'created_at',
            )
        }),
    )

    readonly_fields = (

    )
    filter_horizontal = (
        'categories',
    )

    inlines = [
        PhotoInline,
    ]

    def photos_count(self, obj):
        return obj.photos.count()

    photos_count.short_description = 'Фото'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'post',
        'license_type',
        'camera_model',
        'file_format',
        'resolution',
        'created_at',
    )

    list_filter = (
        'license_type',
        'file_format',
        'created_at',
    )

    search_fields = (
        'title',
        'short_description',
        'post__title',
        'camera_model',
    )

    fieldsets = (
        ('Связь с публикацией', {
            'fields': (
                'post',
            )
        }),

        ('Изображение', {
            'fields': (
                'image',
                'title',
                'short_description',
            )
        }),

        ('Права использования', {
            'fields': (
                'license_type',
                'price_note',
            )
        }),

        ('Техническая информация', {
            'fields': (
                'camera_model',
                'file_format',
                'resolution',
            )
        }),

        ('Служебное', {
            'fields': (
                'created_at',
            )
        }),
    )

    readonly_fields = (

    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    prepopulated_fields = {
        'slug': ('name',),
    }