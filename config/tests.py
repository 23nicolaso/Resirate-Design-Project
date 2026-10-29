from django.test import SimpleTestCase
from django.urls import reverse


class PlaceholderRouteTests(SimpleTestCase):
    # SimpleTestCase forbids DB access: unfinished endpoints must not touch data.
    routes = [
        ("accounts:register", {}, ["get", "post"]),
        ("accounts:login", {}, ["get", "post"]),
        ("accounts:logout", {}, ["post"]),
        ("accounts:dashboard", {}, ["get"]),
        ("accounts:my_reviews", {}, ["get"]),
        ("accounts:my_issues", {}, ["get"]),
        ("reviews:review_create", {"building_pk": 1}, ["get", "post"]),
        ("reviews:review_edit", {"pk": 1}, ["get", "post"]),
        ("reviews:review_delete", {"pk": 1}, ["get", "post"]),
        ("reviews:issue_create", {"building_pk": 1}, ["get", "post"]),
        ("reviews:issue_edit", {"pk": 1}, ["get", "post"]),
        ("reviews:issue_delete", {"pk": 1}, ["get", "post"]),
        ("moderation:report_review", {"pk": 1}, ["get", "post"]),
        ("moderation:report_issue", {"pk": 1}, ["get", "post"]),
        ("moderation:queue", {}, ["get"]),
        ("moderation:report_detail", {"pk": 1}, ["get"]),
        ("moderation:resolve_report", {"pk": 1}, ["post"]),
    ]

    def test_stubs_are_explicit_and_reject_unsupported_methods(self):
        for name, kwargs, allowed in self.routes:
            url = reverse(name, kwargs=kwargs)
            for method in ["get", "post", "put", "patch", "delete"]:
                with self.subTest(route=name, method=method):
                    response = getattr(self.client, method)(url)
                    if method in allowed:
                        self.assertEqual(response.status_code, 501)
                        self.assertEqual(response.json()["status"], "not_implemented")
                    else:
                        self.assertEqual(response.status_code, 405)
