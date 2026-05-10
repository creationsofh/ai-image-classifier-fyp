from django.contrib import admin
from django.db.models import Avg, Count
from django.utils.html import format_html

from .models import (
    Prediction,
    LandingContent,
    PredictionLog,
    AIModelSettings
)


# =========================
# PREDICTION ADMIN
# =========================

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'label',
        'confidence',
        'model_used',
        'prediction_time',
        'uploaded_at',
        'image_preview',
    )

    list_filter = (
        'label',
        'model_used',
        'uploaded_at',
    )

    search_fields = (
        'label',
        'user__username',
        'model_used',
    )

    ordering = (
        '-uploaded_at',
    )

    readonly_fields = (
        'uploaded_at',
        'image_preview',
    )

    # =========================
    # IMAGE PREVIEW
    # =========================

    def image_preview(self, obj):

        if obj.image:

            return format_html(
                '<img src="{}" width="90" style="border-radius:10px;" />',
                obj.image.url
            )

        return "No Image"

    image_preview.short_description = "Preview"

    # =========================
    # GLOBAL ANALYTICS
    # =========================

    def changelist_view(
        self,
        request,
        extra_context=None
    ):

        extra_context = extra_context or {}

        qs = Prediction.objects.all()

        total_predictions = qs.count()

        avg_confidence = qs.aggregate(
            Avg('confidence')
        )['confidence__avg'] or 0

        avg_speed = qs.aggregate(
            Avg('prediction_time')
        )['prediction_time__avg'] or 0

        top_label = (
            qs.values('label')
            .annotate(total=Count('label'))
            .order_by('-total')
            .first()
        )

        unique_users = (
            qs.values('user')
            .distinct()
            .count()
        )

        model_stats = (
            qs.values('model_used')
            .annotate(total=Count('model_used'))
            .order_by('-total')
        )

        extra_context['total_predictions'] = (
            total_predictions
        )

        extra_context['avg_confidence'] = round(
            avg_confidence,
            2
        )

        extra_context['avg_speed'] = round(
            avg_speed,
            2
        )

        extra_context['top_label'] = (

            top_label['label']

            if top_label

            else 'N/A'
        )

        extra_context['unique_users'] = (
            unique_users
        )

        extra_context['model_stats'] = (
            model_stats
        )

        return super().changelist_view(
            request,
            extra_context=extra_context
        )


# =========================
# PREDICTION LOG ADMIN
# =========================

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'model_used',
        'prediction_label',
        'confidence',
        'prediction_time',
        'created_at',
    )

    list_filter = (
        'model_used',
        'created_at',
    )

    search_fields = (
        'prediction_label',
        'user__username',
    )

    ordering = (
        '-created_at',
    )


# =========================
# LANDING PAGE CMS ADMIN
# =========================

@admin.register(LandingContent)
class LandingContentAdmin(admin.ModelAdmin):

    list_display = (
        'site_name',
    )


# =========================
# AI MODEL SETTINGS ADMIN
# =========================

@admin.register(AIModelSettings)
class AIModelSettingsAdmin(admin.ModelAdmin):

    list_display = (
        'active_model',
        'updated_at',
    )

    readonly_fields = (
        'updated_at',
    )