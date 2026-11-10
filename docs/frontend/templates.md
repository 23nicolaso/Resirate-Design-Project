# Frontend templates: what each view needs to pass

The templates below are ready. Routes marked **501** still return
`not_implemented(...)`; to show the page, the view only needs to `render()`
the template with the context listed. Field names follow `reviews/forms.py`
and Django's built-in auth forms, so the forms can be passed in unchanged.

| Route (name) | Template | Context |
| --- | --- | --- |
| `buildings:search` | `buildings/search.html` | `query`, `buildings`, `addresses`, `search_error` (unchanged) |
| `buildings:detail` | `buildings/detail.html` | `building` (required). Optional `average_rating` (float 1–5): shown as the building's overall score when provided. Reviews and issue reports are read from `building.reviews` / `building.issue_reports`. |
| `accounts:login` **501** | `accounts/login.html` | `form` (`AuthenticationForm`), optional `next` |
| `accounts:register` **501** | `accounts/register.html` | `form` (`UserCreationForm` subclass for `accounts.User`) |
| `reviews:review_create` **501** | `reviews/review_form.html` | `building`, `form` (`ReviewForm`), `ratings_formset` (`ReviewRatingsFormSet(initial=ReviewRatingsFormSet.required_initial())`) |
| `reviews:review_edit` **501** | `reviews/review_form.html` | same as create, plus `review` |
| `reviews:review_delete` **501** (GET) | `reviews/review_confirm_delete.html` | `review` |
| `reviews:issue_create` **501** | `reviews/issue_form.html` | `building`, `form` (`IssueReportForm`) |
| `reviews:issue_edit` **501** | `reviews/issue_form.html` | same as create, plus `issue` |
| `reviews:issue_delete` **501** (GET) | `reviews/issue_confirm_delete.html` | `issue` |

All forms POST back to their own route and include `{% csrf_token %}`.
The ratings formset uses Django's default `form` prefix
(`form-0-category`, `form-0-score`, ...).

`base.html` shows Django `messages` as Bootstrap alerts, so views can use
`messages.success(request, "...")` after a successful POST.

## Shared pieces

- `templates/components/`: `search_bar.html`, `building_card.html`,
  `rating_display.html`, `form_field.html`, `form_errors.html`,
  `empty_state.html` (usage is documented at the top of each file).
- `static/css/styles.css`: shared styles on top of Bootstrap 5.3.8.
- `static/js/main.js`: CSRF/fetch helpers and Bootstrap classes for Django
  form widgets inside `<form class="rr-form">`.
- `static/js/address-search.js`: address autocomplete on the search page.
  It calls `buildings:address_suggestions` and then POSTs the chosen
  `selection_token` to `buildings:resolve_address`, then opens the returned
  building URL.
