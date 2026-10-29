"""Shared custom error responses for ResiRate."""

from django.http import JsonResponse


def not_implemented(feature, requirements):
    """Make unfinished routes explicit without reading or changing user data."""
    return JsonResponse(
        {"status": "not_implemented", "feature": feature,
         "requirements": requirements},
        status=501,
    )
