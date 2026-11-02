import json
import logging
from dataclasses import asdict

from django.core import signing
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .geosearch import ThirdPartyServiceError, search_addresses
from .models import Building

logger = logging.getLogger(__name__)

SALT = "buildings.address-selection.v1"


def address_suggestion(address):
    """Sign provider data so resolution never trusts client-supplied fields."""
    data = asdict(address)
    data["selection_token"] = signing.dumps(data, salt=SALT, compress=True)
    return data


def search(request):
    query = request.GET.get("q", "").strip()
    buildings = Building.objects.none()

    addresses = []
    search_error = None
    if query:
        buildings = Building.objects.filter(
            address__icontains=query
        )[:50]
        try:
            addresses = search_addresses(query)
        except ThirdPartyServiceError as exc:
            logger.warning("GeoSearch request failed", exc_info=True)
            search_error = str(exc)

    return render(request, "buildings/search.html", {
        "query": query,
        "buildings": buildings,
        "addresses": addresses,
        "search_error": search_error,
    })


def detail(request, pk):
    building = get_object_or_404(Building, pk=pk)

    return render(request, "buildings/detail.html", {
        "building": building,
    })

@require_GET
def address_suggestions(request):
    query = request.GET.get("q", "").strip()
    if len(query) > 255:
        return JsonResponse({"error": "Please enter an address of 255 characters or fewer."}, status=400)
    if len(query) < 3:
        return JsonResponse({"suggestions": []})
    try:
        addresses = search_addresses(query, autocomplete=True)
    except ThirdPartyServiceError as exc:
        logger.warning("GeoSearch autocomplete failed", exc_info=True)
        return JsonResponse({"error": str(exc)}, status=503)
    suggestions = [address_suggestion(a) for a in addresses if (
        a.provider_id and a.address and len(a.address) <= 255
        and a.borough in {"Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"}
        and len(a.zip_code) <= 5
    )]
    return JsonResponse({"suggestions": suggestions})


@require_POST
def resolve_address(request):
    try:
        data = json.loads(request.body) if request.content_type == "application/json" else request.POST
        token = data.get("selection_token") if isinstance(data, dict) or hasattr(data, "get") else None
        if not isinstance(token, str) or not token or len(token) > 8192:
            raise ValueError("Invalid selection token")
        address = signing.loads(token, salt=SALT, max_age=900)
        building, created = Building.objects.from_address(address)
    except (ValueError, UnicodeDecodeError, signing.BadSignature):
        return JsonResponse({"error": "Please select an address again; the selection is invalid or expired."}, status=400)
    return JsonResponse({"building_id": building.pk, "created": created,
                         "url": reverse("buildings:detail", args=[building.pk])},
                        status=201 if created else 200)
