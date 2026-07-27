from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from gallery.views_auth import PhotoBankLoginView


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "accounts/login/",
        PhotoBankLoginView.as_view(),
        name="login",
    ),

    path(
        "accounts/logout/",
        LogoutView.as_view(next_page="/"),
        name="logout",
    ),

    path("legal/", include("legal.urls")),
    path("", include("gallery.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )