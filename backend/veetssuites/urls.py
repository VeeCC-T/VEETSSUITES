"""
URL configuration for veetssuites project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("accounts.urls")),
    path("api/portfolio/", include("portfolios.urls")),
    path("api/pharmxam/", include("exams.urls")),  # PHARMXAM exam system
    path("api/payments/", include("payments.urls")),
    path("api/hub3660/", include("hub3660.urls")),  # HUB3660 course system
    path("api/healthee/", include("healthee.urls")),  # HEALTHEE consultation system
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
