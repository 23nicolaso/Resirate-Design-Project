"""Sample request/response JSON for review and issue report endpoints.

Single source of truth for the placeholder views' `contract` payloads and
for docs/api/reviews_issues.md. Keep both in sync with this module.
"""

RATING_CATEGORIES = [
    {"key": "maintenance", "label": "Maintenance & Repairs", "display_order": 1},
    {"key": "cleanliness", "label": "Cleanliness", "display_order": 2},
    {"key": "noise", "label": "Noise Level", "display_order": 3},
    {"key": "management", "label": "Management Responsiveness", "display_order": 4},
    {"key": "safety", "label": "Safety & Security", "display_order": 5},
]

RATING_SCALE = {"min": 1, "max": 5, "meaning": {1: "Very poor", 5: "Excellent"}}

REVIEW_CREATE = {
    "request": {
        "body": "Responsive management, but the elevator is often out.",
        "ratings": {
            "maintenance": 3,
            "cleanliness": 4,
            "noise": 3,
            "management": 5,
            "safety": 4,
        },
    },
    "response_201": {
        "id": 42,
        "building_id": 7,
        "author": "jdoe",
        "body": "Responsive management, but the elevator is often out.",
        "overall_rating": 3.8,
        "ratings": [
            {"category": "maintenance", "label": "Maintenance & Repairs", "score": 3},
            {"category": "cleanliness", "label": "Cleanliness", "score": 4},
            {"category": "noise", "label": "Noise Level", "score": 3},
            {"category": "management", "label": "Management Responsiveness", "score": 5},
            {"category": "safety", "label": "Safety & Security", "score": 4},
        ],
        "created_at": "2026-11-01T18:32:00Z",
        "updated_at": "2026-11-01T18:32:00Z",
    },
    "response_400": {
        "status": "error",
        "errors": {
            "ratings": {"safety": ["This field is required."]},
            "body": ["Ensure this value has at most 2000 characters."],
        },
    },
    "response_409": {
        "status": "error",
        "errors": {"__all__": ["You have already reviewed this building."]},
    },
}

REVIEW_EDIT = {
    "request": {
        "body": "Updated: the elevator was finally fixed.",
        "ratings": {
            "maintenance": 4,
            "cleanliness": 4,
            "noise": 3,
            "management": 5,
            "safety": 4,
        },
    },
    "response_200": {**REVIEW_CREATE["response_201"], "overall_rating": 4.0},
    "response_403": {
        "status": "error",
        "errors": {"__all__": ["You can only edit your own review."]},
    },
    "response_400": REVIEW_CREATE["response_400"],
}

REVIEW_DELETE = {
    "request": {},
    "response_200": {"status": "deleted", "id": 42},
    "response_403": REVIEW_EDIT["response_403"],
}

ISSUE_CREATE = {
    "request": {
        "title": "No heat in unit 4B",
        "description": "Heat has been out since Monday, super has not responded.",
    },
    "response_201": {
        "id": 18,
        "building_id": 7,
        "reporter": "jdoe",
        "title": "No heat in unit 4B",
        "description": "Heat has been out since Monday, super has not responded.",
        "status": "open",
        "created_at": "2026-11-01T18:40:00Z",
        "updated_at": "2026-11-01T18:40:00Z",
    },
    "response_400": {
        "status": "error",
        "errors": {"title": ["This field is required."]},
    },
}

ISSUE_EDIT = {
    "request": {
        "title": "No heat in unit 4B",
        "description": "Heat restored Wednesday; filing for the record.",
    },
    "response_200": {**ISSUE_CREATE["response_201"], "status": "open"},
    "response_403": {
        "status": "error",
        "errors": {"__all__": ["You can only edit your own issue report."]},
    },
    "response_400": ISSUE_CREATE["response_400"],
}

ISSUE_DELETE = {
    "request": {},
    "response_200": {"status": "deleted", "id": 18},
    "response_403": ISSUE_EDIT["response_403"],
}
