from django.shortcuts import get_object_or_404, render

from .models import Building


def search(request):
    query = request.GET.get("q", "").strip()
    buildings = Building.objects.none()

    if query:
        buildings = Building.objects.filter(
            address__icontains=query
        )[:50]

    return render(request, "buildings/search.html", {
        "query": query,
        "buildings": buildings,
    })


def detail(request, pk):
    building = get_object_or_404(Building, pk=pk)

    return render(request, "buildings/detail.html", {
        "building": building,
    })