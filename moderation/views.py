from django.views.decorators.http import require_GET, require_http_methods, require_POST

from config.errors import not_implemented


@require_http_methods(["GET", "POST"])
def report_review(request, pk):
    return not_implemented("Flag a review", ["FR-06.1", "FR-06.10", "FR-06.11"])


@require_http_methods(["GET", "POST"])
def report_issue(request, pk):
    return not_implemented("Flag an issue report", ["FR-06.1", "FR-06.10", "FR-06.11"])


@require_GET
def queue(request):
    return not_implemented("Moderation queue", ["FR-06.4", "FR-06.8"])


@require_GET
def report_detail(request, pk):
    return not_implemented("Moderation report detail", ["FR-06.5", "FR-06.8"])


@require_POST
def resolve_report(request, pk):
    return not_implemented("Resolve flagged content", ["FR-06.6", "FR-06.7", "FR-06.12"])
