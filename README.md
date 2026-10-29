# ResiRate

Residential building reviews for NYC. Uses Django, PostgreSQL, and HTML templates styled with Bootstrap. Django and PostgreSQL run in Docker for local development.

## Run locally

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
