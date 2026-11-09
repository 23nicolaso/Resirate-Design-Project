from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

MIN_SCORE = 1
MAX_SCORE = 5


class RatingCategory(models.Model):
    """One of the fixed dimensions a resident rates a building on.

    Seeded by a data migration; not user-creatable.
    """

    key = models.SlugField(max_length=30, unique=True)
    label = models.CharField(max_length=50)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "key"]
        verbose_name_plural = "rating categories"

    def __str__(self):
        return self.label


class Review(models.Model):
    """A resident's written review of a building, with per-category ratings."""

    building = models.ForeignKey(
        "buildings.Building", on_delete=models.CASCADE, related_name="reviews"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    body = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["building", "author"], name="one_review_per_author_per_building"
            ),
        ]

    def __str__(self):
        return f"Review of {self.building} by {self.author}"

    @property
    def overall_rating(self):
        """Arithmetic mean of this review's category scores, rounded to 1 decimal."""
        scores = list(self.ratings.values_list("score", flat=True))
        if not scores:
            return None
        return round(sum(scores) / len(scores), 1)


class Rating(models.Model):
    """A single category score (1-5) attached to a review."""

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="ratings")
    category = models.ForeignKey(
        RatingCategory, on_delete=models.PROTECT, related_name="ratings"
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_SCORE), MaxValueValidator(MAX_SCORE)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["review", "category"], name="one_score_per_category_per_review"
            ),
        ]

    def __str__(self):
        return f"{self.category}: {self.score}"


class IssueReport(models.Model):
    """A dated report of a problem at a building, filed by a resident."""

    STATUS_OPEN = "open"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    building = models.ForeignKey(
        "buildings.Building", on_delete=models.CASCADE, related_name="issue_reports"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="issue_reports"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.building})"
