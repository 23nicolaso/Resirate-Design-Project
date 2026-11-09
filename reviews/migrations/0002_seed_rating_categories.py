from django.db import migrations

# Inlined rather than imported from reviews.contracts: data migrations must
# stay self-contained so they replay the same way even if contracts.py
# changes later. Keep this list in sync with reviews.contracts.RATING_CATEGORIES.
RATING_CATEGORIES = [
    {"key": "maintenance", "label": "Maintenance & Repairs", "display_order": 1},
    {"key": "cleanliness", "label": "Cleanliness", "display_order": 2},
    {"key": "noise", "label": "Noise Level", "display_order": 3},
    {"key": "management", "label": "Management Responsiveness", "display_order": 4},
    {"key": "safety", "label": "Safety & Security", "display_order": 5},
]


def seed_categories(apps, schema_editor):
    RatingCategory = apps.get_model("reviews", "RatingCategory")
    for category in RATING_CATEGORIES:
        RatingCategory.objects.update_or_create(
            key=category["key"],
            defaults={
                "label": category["label"],
                "display_order": category["display_order"],
            },
        )


def unseed_categories(apps, schema_editor):
    RatingCategory = apps.get_model("reviews", "RatingCategory")
    RatingCategory.objects.filter(
        key__in=[category["key"] for category in RATING_CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
