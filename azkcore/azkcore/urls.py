from django.contrib import admin
from django.urls import path, include
from apps.accounts.views import login, logout
from apps.home.views import dashboard_view
from apps.home_fuctions.scan_network.views import scan_network_view
from apps.home_fuctions.dns_subfinder.views import dns_subfinder_view, cancelar_dns_scan_view
from apps.home_fuctions.settings.views import settings_view
from apps.home_fuctions.settings_profile.views import profile_view
from apps.logs.views import logs_view
from apps.home_fuctions.scan_web.views import scan_web_view, cancelar_escaneo_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", login, name="login"),
    path("auth/logout/", logout, name="logout"),
    path("home/dashboard/", dashboard_view, name="dashboard"),
    path("home/messages/", include('apps.home_fuctions.messages.urls')),
    path("home/scan-network/", scan_network_view, name="scan_network"),
    path("home/scan-web/", scan_web_view, name="scan_web"),
    path("home/scan-web/<int:job_id>/cancelar/", cancelar_escaneo_view, name="cancelar_scan_web"),
    path("home/dns-subfinder/", dns_subfinder_view, name="dns_subfinder"),
    path("home/settings/", settings_view, name="settings"),
    path("home/profile/", profile_view, name="profile"),
    path("home/logs/", logs_view, name="logs"),
    path("home/dns-subfinder/<uuid:pk>/cancelar/", cancelar_dns_scan_view, name="cancelar_dns_scan")
]
