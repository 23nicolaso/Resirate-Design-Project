# ResiRate

Residential building reviews for NYC. Uses Django, PostgreSQL, and HTML templates styled with Bootstrap. Django and PostgreSQL run in Docker for local development.

## Install tools (first time only)

Skip anything you already have installed.

1. Install [Git](https://git-scm.com/install/windows) using the default installer options. It lets you clone the repository and share changes.
2. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/), using the WSL 2 backend. If Docker asks for WSL installation, open PowerShell as administrator, run `wsl --install`, and restart Windows if prompted. If WSL needs updating, run `wsl --update`. Start Docker Desktop and wait until its engine is running; use Linux containers for this project.
3. Install an editor such as [VS Code](https://code.visualstudio.com/download), or use your existing editor. In VS Code, choose File > Open Folder and select the cloned project folder.
4. Reopen your terminal after installation and check:

```powershell
git --version
docker --version
docker compose version
docker info
```

The first three commands should print versions; `docker info` should show server information without a connection error. Docker Desktop includes Compose. Python, Django, PostgreSQL, and their dependencies are installed inside the containers; you do not need separate local installations. Bootstrap CSS is loaded by the page from a CDN.

To get the code, copy this repository's clone URL from GitHub's Code button and run `git clone <repository-url>` with the actual URL, then open the downloaded folder. Continue with Run locally below.

## Run locally

Both frontend and backend developers use this same Docker setup. Clone the repository with Git, open it in your editor, and run all commands below from the folder containing `compose.yaml` and `manage.py`.

Install and start Docker Desktop. From the project folder, run:

```powershell
docker compose up --build -d
```

Docker installs Python dependencies, waits for PostgreSQL, applies migrations, and starts Django. No local Python installation, virtual environment, or `.env` file is required for this setup. The first build takes longer while images and dependencies download.

Open http://127.0.0.1:8001/. To add sample buildings through http://127.0.0.1:8001/admin/, first create an administrator:

```powershell
docker compose exec web python manage.py createsuperuser
```

For later sessions, run `docker compose up -d`. Run `docker compose up --build -d` after dependency or Dockerfile changes. Python changes reload automatically; refresh the browser after template or static-file changes.

View startup errors with `docker compose logs -f web`. Use `docker compose stop` to stop both services. The Docker volume keeps database data between restarts. Each teammate has their own database; Git does not share its contents. The website uses port 8001 on your computer to avoid conflicts with a local Django server on port 8000.

## Frontend workflow

1. Complete Run locally above. Open http://127.0.0.1:8001/ in your browser. There is no separate frontend server or npm install; Django serves the HTML pages.
2. Edit `templates/base.html` for shared navigation/layout, `templates/buildings/search.html` for search, and `templates/buildings/detail.html` for the building profile. New pages go under `templates/<app>/`.
3. Create CSS files under `static/css/` and JavaScript files under `static/js/` as needed. Bootstrap CSS is already included in `base.html`. Load your own files with Django's `{% static %}` tag as shown below.
4. Save changes and refresh the browser. Open pages through Django's URL, rather than opening HTML files directly or using VS Code Live Server, so template tags render correctly.
5. To see sample building data, create a superuser using the command above and add buildings through `/admin/`. Your local database starts independently of other teammates' databases.
6. For a new page, agree with the backend developer on its route name, template filename, context variables, form fields, and error messages. Use the route/page example below to connect a template. Most existing routes still return 501; creating a template alone will not make those views render it. Have the backend developer connect the view when the page is ready, or agree on a temporary GET-only preview using sample data.
7. Before submitting changes, check desktop/mobile layouts, keyboard navigation, labels, and empty/error states. Commit templates, CSS, and JavaScript on your feature branch and open a pull request.

Use named links such as `{% url 'accounts:login' %}`. Forms that submit changes use POST and include `{% csrf_token %}`. Check with the backend developer before choosing field names; the view/form must accept those same names.

## Backend workflow

1. Complete Run locally above. Run Django management commands inside the `web` container with `docker compose exec web python manage.py ...`.
2. Find the feature's route in its app's `urls.py` and its handler in `views.py`. Apps are `accounts`, `buildings`, `reviews`, and `moderation`; `config/urls.py` connects them. The route inventory below lists the existing scaffold.
3. Agree on the template/context/form contract with the frontend developer. Implement the view, validation, and database operations, replacing its `not_implemented(...)` response. Put shared custom error responses in `config/errors.py`.
4. Add login, ownership, and moderation permission checks as appropriate. Keep GET requests read-only; perform mutations through POST. Keep private account data out of public responses.
5. When changing models, follow Change database tables below and commit the generated migrations. Review and moderation models are currently abstract outlines; they must have fields and constraints before becoming concrete models. Use `settings.AUTH_USER_MODEL` for relationships to users.
6. If adding a Python dependency, add a pinned compatible version to `requirements.txt`, then run `docker compose up --build -d`.
7. Add tests for the feature and run the commands below before opening a pull request. Update `config/tests.py` as routes become implemented: it currently expects scaffold routes to return 501. Replace those expectations with tests for real behavior and permissions.

```powershell
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web python manage.py test
```

After either team pulls changes, run:

```powershell
docker compose up --build -d
docker compose exec web python manage.py migrate
```

This rebuilds dependencies if needed and applies new migrations even if the web container was already running. Existing local database records remain in the Docker volume.

## Add a route and frontend page

A route connects a URL to a Python view. The view can render an HTML template.

For example, add this view in `buildings/views.py`:

```python
def about(request):
    return render(request, "buildings/about.html")
```

Add this entry inside the existing `urlpatterns` list in `buildings/urls.py`:

```python
path("about/", views.about, name="about"),
```

Create `templates/buildings/about.html`:

```html
{% extends "base.html" %}

{% block content %}
  <h1>About ResiRate</h1>
  <p>Find and share information about NYC residential buildings.</p>
{% endblock %}
```

Visit http://127.0.0.1:8001/about/. Link to the page from another template with:

```html
<a href="{% url 'buildings:about' %}">About</a>
```

`templates/base.html` holds the shared layout. Put page HTML in `templates/`, CSS in `static/css/`, and JavaScript in `static/js/`. Load your own static files in a template like this:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/styles.css' %}">
<script src="{% static 'js/main.js' %}" defer></script>
```

For routes in another app, create its `urls.py` and include it in `config/urls.py`. For example, `path("reviews/", include("reviews.urls"))` gives that app's routes a `/reviews/` prefix. Keep the existing routes.

## Change the database connection

The `web.environment` section in `compose.yaml` supplies the `DB_*` connection values read by `config/settings.py`. For a different database, update those values and run `docker compose up -d` to recreate the web container. Startup applies migrations to the selected database; it does not copy existing data. For hosted credentials, use Compose variable substitution with an ignored `.env` file rather than committing secrets. Configure SSL in Django if the provider requires it.

Inside Docker, Django connects to host `db` on port `5432`. If connecting from a tool on your computer, such as pgAdmin, use host `127.0.0.1` and port `5433`. Compose's web environment overrides any existing local `.env` database settings.

Changing `POSTGRES_USER`, `POSTGRES_PASSWORD`, or `POSTGRES_DB` in Compose does not update an already initialized database volume. Existing credentials and databases must be changed within PostgreSQL. Do not delete the volume unless you intend to lose its data.

## Change database tables

Edit the appropriate app's `models.py`, then run:

```powershell
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Commit the generated migration files so teammates can apply the same changes. Use `settings.AUTH_USER_MODEL` when adding relationships to users; this project uses `accounts.User`.

## Before committing

Run `docker compose exec web python manage.py check` and `docker compose exec web python manage.py test`. Commit source code and migrations. Keep `.env`, `.venv/`, and private credentials out of Git. The credentials in Compose and Django's development server are for local development only.

## Backend route scaffold

Shared custom error responses belong in `config/errors.py`. Views import `not_implemented` from that module for unfinished features.

Search and building profiles already have basic implementations. All other routes below are placeholders returning HTTP 501 with a feature description. They do not authenticate, authorize, query, or save anything yet. Standard Django CSRF protection still applies to POST requests. When implementing forms, include `{% csrf_token %}` and add login/ownership/moderation permission checks before accessing data.

These are Django page/form routes: GET displays information or a form; POST performs changes. Deletion GET requests will only display confirmation when implemented. Registration/login are public; account/contribution/reporting actions require login; moderation queue/detail/resolution require explicit moderation permission.

| Path | Methods | Purpose |
| --- | --- | --- |
| `/` | GET | Building address search (basic implementation) |
| `/buildings/<pk>/` | GET | Building profile (basic implementation) |
| `/accounts/register/` | GET, POST | Registration |
| `/accounts/login/` | GET, POST | Login |
| `/accounts/logout/` | POST | Logout |
| `/accounts/` | GET | Account dashboard |
| `/accounts/reviews/` | GET | Own reviews |
| `/accounts/issues/` | GET | Own issue reports |
| `/buildings/<building_pk>/reviews/new/` | GET, POST | Submit review and category ratings |
| `/reviews/<pk>/edit/` | GET, POST | Edit own review and ratings |
| `/reviews/<pk>/delete/` | GET, POST | Confirm/delete own review |
| `/buildings/<building_pk>/issues/new/` | GET, POST | Submit issue report |
| `/issues/<pk>/edit/` | GET, POST | Edit own issue report |
| `/issues/<pk>/delete/` | GET, POST | Confirm/delete own issue report |
| `/moderation/reviews/<pk>/report/` | GET, POST | Flag a review |
| `/moderation/issues/<pk>/report/` | GET, POST | Flag an issue report |
| `/moderation/` | GET | Flagged-content queue |
| `/moderation/reports/<pk>/` | GET | Flagged-content details |
| `/moderation/reports/<pk>/resolve/` | POST | Keep/remove content and resolve flags |
| `/admin/` | Django admin | Existing administration interface |

Profile pages will include public reviews, ratings, and dated issue reports; those do not need separate routes initially. Rating updates belong to review submissions, and aggregate calculation belongs in backend logic. External public-data integration remains optional and has no public mutation route.

`reviews/models.py` outlines Review, RatingCategory, Rating, and IssueReport. `moderation/models.py` outlines ContentReport and ModerationAction. These are abstract placeholders: they have no tables, fields, or persistence behavior yet. When implementing these models, add their fields and remove `abstract = True` before generating migrations. The existing User and Building models remain concrete. Decide the rating scale, aggregate calculation, category requirements, and review-per-user/building policy before implementing those models.
