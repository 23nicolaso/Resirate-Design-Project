from django.views.decorators.http import require_http_methods

from config.errors import not_implemented


@require_http_methods(["GET", "POST"])
def review_create(request, building_pk):
    return not_implemented("Create review and ratings", ["FR-03", "FR-02.5"])


@require_http_methods(["GET", "POST"])
def review_edit(request, pk):
    return not_implemented("Edit own review and ratings", ["FR-03.6", "FR-05.7"])


@require_http_methods(["GET", "POST"])
def review_delete(request, pk):
    return not_implemented("Delete own review", ["FR-03.6", "NFR-04.3"])


@require_http_methods(["GET", "POST"])
def issue_create(request, building_pk):
    return not_implemented("Create issue report", ["FR-04"])


@require_http_methods(["GET", "POST"])
def issue_edit(request, pk):
    return not_implemented("Edit own issue report", ["FR-04.7", "FR-05.7"])


@require_http_methods(["GET", "POST"])
def issue_delete(request, pk):
    return not_implemented("Delete own issue report", ["FR-04.7", "FR-05.7"])
