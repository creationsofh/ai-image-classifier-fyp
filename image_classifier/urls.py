from django.contrib import admin
from django.urls import path

from classifier import views
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # LANDING PAGE
    # =========================
    path('', views.landing),

    # =========================
    # DASHBOARD
    # =========================
    path('dashboard/', views.index),

    # =========================
    # HISTORY
    # =========================
    path('history/', views.history),

    # =========================
    # API DOCS
    # =========================
    path('api/docs/', views.api_docs),

    # =========================
    # API PREDICT
    # =========================
    path('api/predict/', views.api_predict),

    # =========================
    # EXPORTS
    # =========================
    path('export/csv/', views.export_csv),

    path('export/pdf/', views.export_pdf),

    # =========================
    # AUTH
    # =========================
    path('register/', views.register),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
    ),

]

# =========================
# MEDIA FILES
# =========================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )