from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from buildings.models import Building

from .forms import IssueReportForm, RatingScoreForm, ReviewForm, ReviewRatingsFormSet
from .models import IssueReport, Rating, RatingCategory, Review

User = get_user_model()


class RatingCategorySeedTests(TestCase):
    def test_five_fixed_categories_are_seeded(self):
        self.assertEqual(RatingCategory.objects.count(), 5)
        self.assertEqual(
            list(RatingCategory.objects.values_list("key", flat=True)),
            ["maintenance", "cleanliness", "noise", "management", "safety"],
        )


class ReviewModelTests(TestCase):
    def setUp(self):
        self.building = Building.objects.create(
            address="1 Main St", borough="Manhattan", zip_code="10001"
        )
        self.user = User.objects.create_user(username="jdoe", password="pw")

    def test_overall_rating_is_mean_of_category_scores(self):
        review = Review.objects.create(building=self.building, author=self.user)
        categories = list(RatingCategory.objects.all())
        for category, score in zip(categories, [3, 4, 3, 5, 4]):
            Rating.objects.create(review=review, category=category, score=score)

        self.assertEqual(review.overall_rating, 3.8)

    def test_overall_rating_is_none_without_ratings(self):
        review = Review.objects.create(building=self.building, author=self.user)
        self.assertIsNone(review.overall_rating)

    def test_one_review_per_author_per_building(self):
        Review.objects.create(building=self.building, author=self.user)
        with self.assertRaises(IntegrityError):
            Review.objects.create(building=self.building, author=self.user)

    def test_one_score_per_category_per_review(self):
        review = Review.objects.create(building=self.building, author=self.user)
        category = RatingCategory.objects.first()
        Rating.objects.create(review=review, category=category, score=4)
        with self.assertRaises(IntegrityError):
            Rating.objects.create(review=review, category=category, score=5)


class ReviewFormTests(TestCase):
    def test_body_over_max_length_is_rejected(self):
        form = ReviewForm(data={"body": "x" * 2001})
        self.assertFalse(form.is_valid())
        self.assertIn("body", form.errors)

    def test_blank_body_is_allowed(self):
        form = ReviewForm(data={"body": ""})
        self.assertTrue(form.is_valid())


class RatingScoreFormTests(TestCase):
    def test_score_out_of_range_is_rejected(self):
        category = RatingCategory.objects.first()
        form = RatingScoreForm(data={"category": category.pk, "score": 6})
        self.assertFalse(form.is_valid())
        self.assertIn("score", form.errors)

    def test_score_in_range_is_valid(self):
        category = RatingCategory.objects.first()
        form = RatingScoreForm(data={"category": category.pk, "score": 3})
        self.assertTrue(form.is_valid())


class ReviewRatingsFormSetTests(TestCase):
    def _formset_data(self, scores_by_category):
        data = {"form-TOTAL_FORMS": str(len(scores_by_category)), "form-INITIAL_FORMS": "0"}
        for i, (category, score) in enumerate(scores_by_category):
            data[f"form-{i}-category"] = str(category.pk)
            data[f"form-{i}-score"] = str(score)
        return data

    def test_rejects_submission_missing_a_category(self):
        categories = list(RatingCategory.objects.all())[:4]  # omit the 5th
        data = self._formset_data([(c, 3) for c in categories])
        formset = ReviewRatingsFormSet(data=data)
        self.assertFalse(formset.is_valid())

    def test_accepts_submission_with_all_categories(self):
        categories = list(RatingCategory.objects.all())
        data = self._formset_data([(c, 3) for c in categories])
        formset = ReviewRatingsFormSet(data=data)
        self.assertTrue(formset.is_valid())


class IssueReportFormTests(TestCase):
    def test_requires_title_and_description(self):
        form = IssueReportForm(data={"title": "", "description": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("description", form.errors)

    def test_valid_submission(self):
        form = IssueReportForm(
            data={"title": "No heat", "description": "Heat out since Monday."}
        )
        self.assertTrue(form.is_valid())


class IssueReportModelTests(TestCase):
    def test_defaults_to_open_status(self):
        building = Building.objects.create(
            address="1 Main St", borough="Manhattan", zip_code="10001"
        )
        user = User.objects.create_user(username="jdoe", password="pw")
        issue = IssueReport.objects.create(
            building=building, reporter=user, title="No heat", description="..."
        )
        self.assertEqual(issue.status, IssueReport.STATUS_OPEN)
