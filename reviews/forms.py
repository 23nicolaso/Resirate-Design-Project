"""Validation schemas for review and issue report submissions.

These Forms play the role Pydantic schemas would in a FastAPI service: they
define and validate the shape of incoming request data before it touches
the database. Views in this app are still placeholders (see views.py); these
forms are the contract those views will validate against once implemented.
"""

from django import forms

from .models import MAX_SCORE, MIN_SCORE, IssueReport, RatingCategory, Review


class ReviewForm(forms.ModelForm):
    """Validates the free-text portion of a review submission."""

    class Meta:
        model = Review
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 4, "maxlength": 2000}),
        }


class RatingScoreForm(forms.Form):
    """Validates a single category's score within a review submission."""

    category = forms.ModelChoiceField(queryset=RatingCategory.objects.all())
    score = forms.IntegerField(min_value=MIN_SCORE, max_value=MAX_SCORE)


class ReviewRatingsFormSet(forms.formset_factory(RatingScoreForm, extra=0)):
    """One RatingScoreForm per existing RatingCategory.

    A review submission must supply a score for every category currently
    defined in RatingCategory -- partial rating sets are rejected.
    """

    @classmethod
    def required_initial(cls):
        return [
            {"category": category.pk}
            for category in RatingCategory.objects.all()
        ]

    def clean(self):
        super().clean()
        categories_submitted = {
            form.cleaned_data["category"].pk
            for form in self.forms
            if form.cleaned_data.get("category")
        }
        required_categories = set(
            RatingCategory.objects.values_list("pk", flat=True)
        )
        missing = required_categories - categories_submitted
        if missing:
            missing_labels = RatingCategory.objects.filter(
                pk__in=missing
            ).values_list("label", flat=True)
            raise forms.ValidationError(
                f"A score is required for: {', '.join(missing_labels)}."
            )


class IssueReportForm(forms.ModelForm):
    """Validates an issue report submission."""

    class Meta:
        model = IssueReport
        fields = ["title", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4, "maxlength": 2000}),
        }
