from django.shortcuts import render, redirect
from .model import predict_image
from .models import (
    Prediction,
    LandingContent,
    PredictionLog
)

import os
import time
import json
import csv

from reportlab.pdfgen import canvas

from django.http import (
    HttpResponse,
    JsonResponse
)

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Count
from django.views.decorators.csrf import csrf_exempt


# =========================
# LANDING PAGE
# =========================

def landing(request):

    content = LandingContent.objects.first()

    if request.user.is_authenticated:
        return redirect('/dashboard/')

    return render(
        request,
        'landing.html',
        {
            'content': content
        }
    )


# =========================
# API DOCS
# =========================

@login_required(login_url='/login/')
def api_docs(request):

    return render(
        request,
        'api_docs.html'
    )


# =========================
# REGISTER
# =========================

def register(request):

    if request.method == 'POST':

        form = UserCreationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('/login/')

    else:

        form = UserCreationForm()

    return render(
        request,
        'register.html',
        {
            'form': form
        }
    )


# =========================
# DASHBOARD
# =========================

@login_required(login_url='/login/')
def index(request):

    context = {}

    user_predictions = Prediction.objects.filter(
        user=request.user
    )

    # =========================
    # USER ANALYTICS
    # =========================

    total_uploads = user_predictions.count()

    avg_confidence = user_predictions.aggregate(
        Avg('confidence')
    )['confidence__avg'] or 0

    most_predicted_qs = (
        user_predictions
        .values('label')
        .annotate(total=Count('label'))
        .order_by('-total')
        .first()
    )

    most_predicted = (
        most_predicted_qs['label']
        if most_predicted_qs
        else 'N/A'
    )

    recent_uploads = (
        user_predictions
        .order_by('-uploaded_at')[:5]
    )

    # =========================
    # CHART DATA
    # =========================

    label_data = (
        user_predictions
        .values('label')
        .annotate(count=Count('label'))
        .order_by('-count')
    )

    chart_labels = [
        item['label']
        for item in label_data
    ]

    chart_label_counts = [
        item['count']
        for item in label_data
    ]

    confidence_qs = (
        user_predictions
        .order_by('-uploaded_at')[:10]
    )

    chart_confidence = [
        round(float(p.confidence), 2)
        for p in confidence_qs
    ][::-1]

    # =========================
    # DEFAULT VALUES
    # =========================

    avg_speed = 0
    model_stats = []

    # =========================
    # ADMIN ANALYTICS
    # =========================

    if request.user.is_superuser:

        avg_speed = PredictionLog.objects.aggregate(
            Avg('prediction_time')
        )['prediction_time__avg'] or 0

        model_stats = (
            PredictionLog.objects
            .values('model_used')
            .annotate(total=Count('model_used'))
        )

        context.update({

            'total_users':
            Prediction.objects.values(
                'user'
            ).distinct().count(),

            'global_predictions':
            Prediction.objects.count(),

            'global_confidence':
            round(
                Prediction.objects.aggregate(
                    Avg('confidence')
                )['confidence__avg'] or 0,
                2
            )

        })

    # =========================
    # CONTEXT
    # =========================

    context.update({

        'total_uploads':
        total_uploads,

        'avg_confidence':
        round(avg_confidence, 2),

        'most_predicted':
        most_predicted,

        'recent_uploads':
        recent_uploads,

        'chart_labels':
        json.dumps(chart_labels),

        'chart_label_counts':
        json.dumps(chart_label_counts),

        'chart_confidence':
        json.dumps(chart_confidence),

        'avg_speed':
        round(avg_speed, 2),

        'model_stats':
        model_stats,

        'active_model':
        'efficientnet',

        'available_models':
        [
            'efficientnet',
            'mobilenet',
            'resnet'
        ]

    })

    # =========================
    # IMAGE PREDICTION
    # =========================

    if request.method == 'POST' and request.FILES.get('image'):

        uploaded_file = request.FILES['image']

        fs = FileSystemStorage()

        filename = fs.save(
            uploaded_file.name,
            uploaded_file
        )

        file_url = fs.url(filename)

        full_path = os.path.join(
            settings.MEDIA_ROOT,
            filename
        )

        try:

            selected_model = request.POST.get(
                "model",
                "efficientnet"
            )

            start_time = time.time()

            result = predict_image(
                full_path,
                selected_model
            )

            end_time = time.time()

            prediction_time = round(
                end_time - start_time,
                2
            )

            label = result.get('label')

            confidence = result.get(
                'confidence',
                0
            )

            top_predictions = result.get(
                'top_predictions',
                []
            )

            top_predictions = sorted(
                top_predictions,
                key=lambda x: x['confidence'],
                reverse=True
            )

            # =========================
            # SAVE PREDICTION
            # =========================

            Prediction.objects.create(

                user=request.user,

                image=uploaded_file,

                label=label,

                confidence=confidence,

                model_used=selected_model,

                prediction_time=prediction_time

            )

            # =========================
            # SAVE LOG
            # =========================

            PredictionLog.objects.create(

                user=request.user,

                model_used=selected_model,

                prediction_label=label,

                confidence=confidence,

                prediction_time=prediction_time

            )

            # =========================
            # UPDATE CONTEXT
            # =========================

            context.update({

                'file_url':
                file_url,

                'label':
                label,

                'confidence':
                confidence,

                'top_predictions':
                top_predictions,

                'prediction_time':
                prediction_time,

                'model_used':
                selected_model

            })

        except Exception as e:

            context['error'] = str(e)

    return render(
        request,
        'index.html',
        context
    )


# =========================
# HISTORY
# =========================

@login_required(login_url='/login/')
def history(request):

    data = Prediction.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    return render(
        request,
        'history.html',
        {
            'data': data
        }
    )


# =========================
# API PREDICT
# =========================

@csrf_exempt
def api_predict(request):

    if request.method != "POST":

        return JsonResponse({

            "success": False,
            "error": "POST method required"

        }, status=400)

    if 'image' not in request.FILES:

        return JsonResponse({

            "success": False,
            "error": "No image uploaded"

        }, status=400)

    uploaded_file = request.FILES['image']

    fs = FileSystemStorage()

    filename = fs.save(
        uploaded_file.name,
        uploaded_file
    )

    full_path = os.path.join(
        settings.MEDIA_ROOT,
        filename
    )

    try:

        selected_model = request.POST.get(
            "model",
            "efficientnet"
        )

        start_time = time.time()

        result = predict_image(
            full_path,
            selected_model
        )

        end_time = time.time()

        prediction_time = round(
            end_time - start_time,
            2
        )

        label = result.get('label')

        confidence = result.get(
            'confidence',
            0
        )

        top_predictions = result.get(
            'top_predictions',
            []
        )

        top_predictions = sorted(
            top_predictions,
            key=lambda x: x['confidence'],
            reverse=True
        )

        # =========================
        # SAVE DATA
        # =========================

        if request.user.is_authenticated:

            Prediction.objects.create(

                user=request.user,

                image=uploaded_file,

                label=label,

                confidence=confidence,

                model_used=selected_model,

                prediction_time=prediction_time

            )

            PredictionLog.objects.create(

                user=request.user,

                model_used=selected_model,

                prediction_label=label,

                confidence=confidence,

                prediction_time=prediction_time

            )

        return JsonResponse({

            "success": True,

            "model_used": selected_model,

            "prediction_time": prediction_time,

            "label": label,

            "confidence": confidence,

            "top_predictions": top_predictions

        })

    except Exception as e:

        return JsonResponse({

            "success": False,

            "error": "Prediction failed",

            "details": str(e)

        }, status=500)


# =========================
# EXPORT CSV
# =========================

@login_required(login_url='/login/')
def export_csv(request):

    response = HttpResponse(
        content_type='text/csv'
    )

    response['Content-Disposition'] = (
        'attachment; filename="predictions.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        'Label',
        'Confidence',
        'Model',
        'Prediction Time',
        'Uploaded At'
    ])

    predictions = Prediction.objects.filter(
        user=request.user
    )

    for item in predictions:

        writer.writerow([

            item.label,

            item.confidence,

            item.model_used,

            item.prediction_time,

            item.uploaded_at

        ])

    return response


# =========================
# EXPORT PDF
# =========================

@login_required(login_url='/login/')
def export_pdf(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="prediction_report.pdf"'
    )

    p = canvas.Canvas(response)

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        180,
        800,
        "AI Prediction Report"
    )

    y = 760

    predictions = Prediction.objects.filter(
        user=request.user
    )

    for item in predictions:

        text = (
            f"{item.label} | "
            f"{item.confidence}% | "
            f"{item.model_used} | "
            f"{item.prediction_time}s"
        )

        p.setFont(
            "Helvetica",
            11
        )

        p.drawString(
            40,
            y,
            text
        )

        y -= 25

        if y < 60:

            p.showPage()

            y = 800

    p.save()

    return response