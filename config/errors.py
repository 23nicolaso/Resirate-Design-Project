"""Shared custom error responses for ResiRate."""

from django.http import JsonResponse


def not_implemented(feature, requirements, contract=None):
    """Make unfinished routes explicit without reading or changing user data.

    `contract`, when given, is a dict of sample request/response JSON for
    this route so frontend work can proceed against the documented shape
    before the view is implemented.
    """
    payload = {
        "status": "not_implemented",
        "feature": feature,
        "requirements": requirements,
    }
    if contract is not None:
        payload["contract"] = contract
    return JsonResponse(payload, status=501)
