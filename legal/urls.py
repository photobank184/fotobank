from django.urls import path

from . import views

app_name = "legal"

urlpatterns = [
    path("", views.index, name="index"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("cookies/", views.cookies, name="cookies"),
    path(
        "contributor-agreement/",
        views.contributor_agreement,
        name="contributor_agreement",
    ),
    path(
        "license-agreement/",
        views.license_agreement,
        name="license_agreement",
    ),
    path("copyright/", views.copyright_policy, name="copyright"),
    path("acceptable-use/", views.acceptable_use, name="acceptable_use"),
    path("ai-content/", views.ai_content, name="ai_content"),
    path("refunds/", views.refund_policy, name="refunds"),
]