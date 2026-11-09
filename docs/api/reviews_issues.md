# Review & Issue Report API Contracts

Covers `reviews/views.py` and the related templates/forms. Matches the
scaffold in `reviews/urls.py` and the route table in the top-level
`README.md`. All routes below currently return `501` via
`config.errors.not_implemented` — implementation is scheduled for Week 3.
Sample JSON in this document is kept in sync with `reviews/contracts.py`,
which the placeholder views import and return live under a `"contract"` key
(hit any route below with `GET` to see it).

## Rating scale

Integer, **1 (very poor) to 5 (excellent)**. No half-points, no 0, no
unrated/null score once a review exists.

## Rating categories

Fixed set, seeded by `reviews/migrations/0002_seed_rating_categories.py`
(not user-creatable):

| Order | Key | Label |
| --- | --- | --- |
| 1 | `maintenance` | Maintenance & Repairs |
| 2 | `cleanliness` | Cleanliness |
| 3 | `noise` | Noise Level |
| 4 | `management` | Management Responsiveness |
| 5 | `safety` | Safety & Security |

A review submission must include a score for **every** category above — no
partial rating sets. This keeps `overall_rating` comparable across reviews.

## Policies

- **One review per (user, building)** — enforced by the
  `one_review_per_author_per_building` DB constraint on `Review`. A second
  submission attempt for a building the user already reviewed must be
  rejected (`409`); the user edits their existing review instead.
- **Unlimited issue reports per (user, building)** — each is independent and
  has its own `status` (`open` / `resolved`).
- `overall_rating` is **not stored** — it's computed as the mean of a
  review's category scores, rounded to 1 decimal (`Review.overall_rating`
  property).
- Only the author/reporter may edit or delete their own review/issue report
  (`403` otherwise). Enforced at the view layer when implemented — not yet
  active on these placeholders.

## Validation summary

| Field | Rule |
| --- | --- |
| `Review.body` | optional, plain text, max 2000 chars |
| `Rating.score` (per category) | required, integer, 1–5 |
| `IssueReport.title` | required, max 150 chars |
| `IssueReport.description` | required, max 2000 chars |

Validation is implemented as Django Forms (the project's equivalent of
Pydantic schemas) in `reviews/forms.py`: `ReviewForm`, `RatingScoreForm` /
`ReviewRatingsFormSet` (enforces all 5 categories present), and
`IssueReportForm`.

---

## Reviews

### `POST /buildings/<building_pk>/reviews/new/`

Auth: login required. `GET` renders the form; `POST` submits it.

Request body:

```json
{
  "body": "Responsive management, but the elevator is often out.",
  "ratings": {
    "maintenance": 3,
    "cleanliness": 4,
    "noise": 3,
    "management": 5,
    "safety": 4
  }
}
```

Response `201`:

```json
{
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
    {"category": "safety", "label": "Safety & Security", "score": 4}
  ],
  "created_at": "2026-11-01T18:32:00Z",
  "updated_at": "2026-11-01T18:32:00Z"
}
```

Response `400` (validation failure — e.g. missing category, body too long):

```json
{
  "status": "error",
  "errors": {
    "ratings": {"safety": ["This field is required."]},
    "body": ["Ensure this value has at most 2000 characters."]
  }
}
```

Response `409` (user already has a review for this building):

```json
{"status": "error", "errors": {"__all__": ["You have already reviewed this building."]}}
```

### `POST /reviews/<pk>/edit/`

Auth: must be the review's author. Same request/response shape as create,
scoped to the existing review. `403` if the requester isn't the author.

### `POST /reviews/<pk>/delete/`

Auth: must be the review's author. `GET` shows a confirmation page, `POST`
deletes.

Response `200`:

```json
{"status": "deleted", "id": 42}
```

### Retrieval (embedded, no dedicated endpoint)

Per the README, reviews aren't fetched through a standalone list endpoint —
they're part of the building detail page context
(`buildings/views.py:detail`). The shape a template (or a future JSON view)
renders per building:

```json
{
  "building": {"id": 7, "address": "123 Main St", "borough": "Manhattan", "zip_code": "10001"},
  "review_count": 12,
  "average_rating": 3.9,
  "reviews": [
    {
      "id": 42,
      "author": "jdoe",
      "body": "Responsive management, but the elevator is often out.",
      "overall_rating": 3.8,
      "ratings": [{"category": "maintenance", "label": "Maintenance & Repairs", "score": 3}],
      "created_at": "2026-11-01T18:32:00Z"
    }
  ]
}
```

---

## Issue reports

### `POST /buildings/<building_pk>/issues/new/`

Auth: login required.

Request body:

```json
{
  "title": "No heat in unit 4B",
  "description": "Heat has been out since Monday, super has not responded."
}
```

Response `201`:

```json
{
  "id": 18,
  "building_id": 7,
  "reporter": "jdoe",
  "title": "No heat in unit 4B",
  "description": "Heat has been out since Monday, super has not responded.",
  "status": "open",
  "created_at": "2026-11-01T18:40:00Z",
  "updated_at": "2026-11-01T18:40:00Z"
}
```

Response `400`:

```json
{"status": "error", "errors": {"title": ["This field is required."]}}
```

### `POST /issues/<pk>/edit/`

Auth: must be the report's reporter. Same shape as create. Editing does not
change `status`; status transitions belong to moderation, not the reporter.
`403` if the requester isn't the reporter.

### `POST /issues/<pk>/delete/`

Auth: must be the report's reporter.

Response `200`:

```json
{"status": "deleted", "id": 18}
```

---

## Open questions for Week 3 implementation

- Should editing a review re-notify/re-flag it for moderation if it was
  previously reported? (Depends on `moderation` app's concrete models.)
- Does deleting a review cascade-delete its `Rating` rows immediately
  (currently `on_delete=CASCADE`, so yes) — confirm this is the desired
  behavior for aggregate recalculation on the building page.
- Issue report `status` is reporter-read-only in this contract; confirm
  moderation is the only actor that can resolve an issue.
