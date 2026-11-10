from django.contrib import admin

from .models import IssueReport, Rating, RatingCategory, Review


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0


@admin.register(RatingCategory)
class RatingCategoryAdmin(admin.ModelAdmin):
    list_display = ["label", "key", "display_order"]
    ordering = ["display_order"]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["building", "author", "overall_rating", "created_at"]
    list_filter = ["building"]
    inlines = [RatingInline]


@admin.register(IssueReport)
class IssueReportAdmin(admin.ModelAdmin):
    list_display = ["title", "building", "reporter", "status", "created_at"]
    list_filter = ["status", "building"]
