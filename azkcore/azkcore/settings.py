from pathlib import Path
from django.templatetags.static import static
from decouple import config
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

API_BEARER_TOKEN = config("API_BEARER_TOKEN", default=None)
API_BASE_URL = config("API_BASE_URL", default="http://127.0.0.1:8000")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g@j1-$b6!ng)-#*1kuu@x4(l4va^r8e1_kx*+rqd7f*7h*x#x4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'azkcore.tech', '192.168.1.16']


# Application definition

INSTALLED_APPS = [
    "unfold",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',
    'apps.home',
    'apps.home_fuctions.messages',
    'apps.home_fuctions.scan_web',
    'apps.home_fuctions.scan_network',
    "apps.logs",
    'apps.home_fuctions.dns_subfinder',
    'apps.home_fuctions.file_scanner',
    'apps.home_fuctions.password_analyzer'
]

UNFOLD = {
    "SITE_TITLE": "AzkCore Tech | Administrator",
    "SITE_HEADER": "AzkCore Security Panel",
    "SITE_SUBHEADER": "Monitoreo y análisis de infraestructura",
    "SITE_URL": "/",
    "SITE_SYMBOL": "shield_with_heart",  # ícono fallback si no hay logo

    "SITE_ICON": {
        "light": lambda request: static("img/favicon.png"),
        "dark": lambda request: static("img/favicon.png"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("img/logo_blue.png"),
        "dark": lambda request: static("img/logo_black.png"),
    },

    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,

    # ------------------------------------------------------------
    # Buscador con comandos (Cmd+K) — mejora mucho la experiencia
    # ------------------------------------------------------------
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },

    # ------------------------------------------------------------
    # PALETA — Tema "cyber" cyan/azul oscuro, look tipo SOC
    # ------------------------------------------------------------
    "COLORS": {
        "base": {
            "50": "248 250 252",
            "100": "241 245 249",
            "200": "226 232 240",
            "300": "203 213 225",
            "400": "148 163 184",
            "500": "100 116 139",
            "600": "71 85 105",
            "700": "51 65 85",
            "800": "30 41 59",
            "900": "15 23 42",
            "950": "2 6 23",
        },
        "primary": {
            "50": "236 254 255",
            "100": "207 250 254",
            "200": "165 243 252",
            "300": "103 232 249",
            "400": "34 211 238",
            "500": "6 182 212",
            "600": "8 145 178",
            "700": "14 116 144",
            "800": "21 94 117",
            "900": "22 78 99",
            "950": "8 51 68",
        },
        "font": {
            "subtle-light": "100 116 139",
            "subtle-dark": "148 163 184",
            "default-light": "30 41 59",
            "default-dark": "226 232 240",
            "important-light": "15 23 42",
            "important-dark": "248 250 252",
        },
    },

    "BORDER_RADIUS": "8px",

    # ------------------------------------------------------------
    # Badge de entorno (dev/staging/prod)
    # ------------------------------------------------------------
    "ENVIRONMENT": "apps.home.admin_utils.environment_callback",


    # ------------------------------------------------------------
    # Dashboard personalizado con KPIs
    # ------------------------------------------------------------
    "DASHBOARD_CALLBACK": "apps.home.admin_utils.dashboard_callback",

    "LOGIN": {
        "image": lambda request: static("img/login-bg.jpg"),
    },

    # ------------------------------------------------------------
    # SIDEBAR — organizado por función, no por app técnica
    # ------------------------------------------------------------
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Panel principal"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "space_dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": _("Reconocimiento DNS"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Subfinder"),
                        "icon": "dns",
                        "link": reverse_lazy("admin:dns_subfinder_dnsscanjob_changelist"),
                    },
                ],
            },
            {
                "title": _("Escaneo y Monitoreo"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Network Scan"),
                        "icon": "radar",
                        "link": reverse_lazy("admin:scan_network_scanjob_changelist"),
                    },
                    {
                        "title": _("Logs del sistema"),
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:logs_logentry_changelist"),
                    },
                ],
            },
            {
                "title": _("Usuarios y permisos"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Usuarios"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Grupos"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'azkcore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'azkcore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# Solo para producción:
# STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_FROM_EMAIL = "no-reply@azkcore.tech"
CONTACT_EMAIL = "azk.os.dev@gmail.com"  # a donde llegan las solicitudes

LOGIN_URL = "login"