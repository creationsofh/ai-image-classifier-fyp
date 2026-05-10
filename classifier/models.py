from django.db import models
from django.contrib.auth.models import User


# =========================
# PREDICTIONS
# =========================

class Prediction(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    image = models.ImageField(
        upload_to='predictions/'
    )

    label = models.CharField(
        max_length=255
    )

    confidence = models.FloatField()

    # seconds taken for prediction
    prediction_time = models.FloatField(
        default=0
    )

    model_used = models.CharField(
        max_length=100,
        default='efficientnet'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.label} ({self.model_used})"


# =========================
# PREDICTION LOG
# =========================

class PredictionLog(models.Model):

    MODEL_CHOICES = [
        ('efficientnet', 'EfficientNet'),
        ('mobilenet', 'MobileNet'),
        ('resnet', 'ResNet'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    model_used = models.CharField(
        max_length=50,
        choices=MODEL_CHOICES
    )

    prediction_label = models.CharField(
        max_length=255
    )

    confidence = models.FloatField()

    prediction_time = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.model_used} - {self.prediction_label}"


# =========================
# LANDING CONTENT
# =========================

class LandingContent(models.Model):

    site_name = models.CharField(
        max_length=200,
        default="CreationsofH AI"
    )

    hero_title = models.CharField(
        max_length=255,
        blank=True
    )

    hero_desc = models.TextField(
        blank=True
    )

    feature_title = models.CharField(
        max_length=255,
        blank=True
    )

    feature_subtitle = models.TextField(
        blank=True
    )

    cta_title = models.CharField(
        max_length=255,
        blank=True
    )

    cta_desc = models.TextField(
        blank=True
    )

    footer_text = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return self.site_name


# =========================
# AI MODEL SETTINGS
# =========================

class AIModelSettings(models.Model):

    MODEL_CHOICES = [

        ('efficientnet', 'EfficientNet'),
        ('mobilenet', 'MobileNet'),
        ('resnet', 'ResNet'),

    ]

    active_model = models.CharField(
        max_length=100,
        choices=MODEL_CHOICES,
        default='efficientnet'
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Active Model: {self.active_model}"