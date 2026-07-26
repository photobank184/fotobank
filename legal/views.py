from django.shortcuts import render


def index(request):
    return render(request, "legal/index.html")


def terms(request):
    return render(request, "legal/terms.html")


def privacy(request):
    return render(request, "legal/privacy.html")


def cookies(request):
    return render(request, "legal/cookies.html")


def contributor_agreement(request):
    return render(request, "legal/contributor_agreement.html")


def license_agreement(request):
    return render(request, "legal/license_agreement.html")


def copyright_policy(request):
    return render(request, "legal/copyright.html")


def acceptable_use(request):
    return render(request, "legal/acceptable_use.html")


def ai_content(request):
    return render(request, "legal/ai_content.html")


def refund_policy(request):
    return render(request, "legal/refunds.html")