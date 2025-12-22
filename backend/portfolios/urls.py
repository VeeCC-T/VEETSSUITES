from django.urls import path
from .views import (
    PortfolioUploadView,
    PortfolioDetailView,
    PortfolioUpdateView,
    PortfolioDeleteView,
    MyPortfolioView
)

app_name = 'portfolios'

urlpatterns = [
    path('upload/', PortfolioUploadView.as_view(), name='portfolio-upload'),
    path('me/', MyPortfolioView.as_view(), name='my-portfolio'),
    path('<int:user_id>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('<int:user_id>/update/', PortfolioUpdateView.as_view(), name='portfolio-update'),
    path('<int:user_id>/delete/', PortfolioDeleteView.as_view(), name='portfolio-delete'),
]
