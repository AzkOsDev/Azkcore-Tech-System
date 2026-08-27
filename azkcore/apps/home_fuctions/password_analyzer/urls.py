from .views import password_analyzer_view, check_breach, save_analysis
from django.urls import path

urlpatterns = [
    # ...
    path('', password_analyzer_view, name='password_analyzer'),
    path('/check-breach/', check_breach, name='check_breach'),
    path('/save/', save_analysis, name='save_password_analysis'),
]