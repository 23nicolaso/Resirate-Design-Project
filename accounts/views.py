from django.views.decorators.http import require_GET, require_http_methods, require_POST

from config.errors import not_implemented


@require_http_methods(["GET", "POST"])
def register(request):
    return not_implemented("Account registration", ["FR-05.1", "NFR-02.1"])


@require_http_methods(["GET", "POST"])
def login(request):
    return not_implemented("Account login", ["FR-05.2", "FR-05.3"])


@require_POST
def logout(request):
    return not_implemented("Account logout", ["FR-05.4"])


@require_GET
def dashboard(request):
    return not_implemented("Account dashboard", ["FR-05.5", "FR-05.8"])


@require_GET
def my_reviews(request):
    return not_implemented("My reviews", ["FR-03.6", "FR-05.5"])


@require_GET
def my_issues(request):
    return not_implemented("My issue reports", ["FR-04.7", "FR-05.5"])
