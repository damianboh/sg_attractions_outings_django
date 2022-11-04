"""
Django settings for sg_attractions_outings project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from configurations import Configuration, values
from datetime import timedelta
import dj_database_url
import os

class Dev(Configuration):

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

    # SECRET_KEY for debug
    # SECURITY WARNING: keep the SECRET_KEY used in production secret!
    SECRET_KEY = 'django-insecure-s!&a3ve&b9t_@t&%#n+6&&8kwv8ly6-$y)2y*($w=km^+_kvrp'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = values.BooleanValue(True)

    BASE_URL = values.Value()
    ALLOWED_HOSTS = []

    # Application definition

    INSTALLED_APPS = [
        'custom_auth',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'crispy_forms',
        'crispy_bootstrap5',
        'attractions',
        "django_celery_results",
        "django_celery_beat",
        "rest_framework",
        "rest_framework.authtoken",
        "drf_yasg",
        'whitenoise.runserver_nostatic',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    ]

    ROOT_URLCONF = 'sg_attractions_outings.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            "DIRS": [BASE_DIR / "templates"],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'sg_attractions_outings.wsgi.application'


    # Database
    # https://docs.djangoproject.com/en/3.2/ref/settings/#databases

    DATABASE_URL = values.Value()
    DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

    # Custom User Model and Registration    
    AUTH_USER_MODEL = "custom_auth.User" 
    ACCOUNT_ACTIVATION_DAYS = 7

    LOGIN_REDIRECT_URL = '/'

    # Password validation
    # https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

    # Crispy Forms
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

    # Email Backend
    EMAIL_BACKEND = values.Value()
    EMAIL_HOST = values.Value()
    EMAIL_PORT = values.Value()
    EMAIL_USE_TLS = values.BooleanValue(True)
    EMAIL_HOST_USER = values.Value()
    EMAIL_HOST_PASSWORD = values.Value()

    # for Django REST Framework
    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "rest_framework.authentication.TokenAuthentication",
            "rest_framework_simplejwt.authentication.JWTAuthentication"
        ],
        "DEFAULT_PAGINATION_CLASS":	"rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 100,
        "DEFAULT_FILTER_BACKENDS": [ 
            "django_filters.rest_framework.DjangoFilterBackend"
        ],
    }

    SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    }

    # Swagger browsable API UI
    SWAGGER_SETTINGS = {
        "SECURITY_DEFINITIONS": {
        "Token": {"type": "apiKey", "name": "Authorization",
        "in": "header"},
        "Basic": {"type": "basic"},
        }
    }


    # Internationalization
    # https://docs.djangoproject.com/en/3.2/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = values.Value("UTC") # read from environment variable

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True


    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/3.2/howto/static-files/

    STATIC_URL = '/static/'

    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]

    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    STATICFILES_STORAGE="whitenoise.storage.CompressedManifestStaticFilesStorage"

    # Default primary key field type
    # https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

    # Tourism Hub External API
    TOURISM_HUB_API_KEY=values.Value()

    # For Celery Async Tasks
    CELERY_RESULT_BACKEND = values.Value("django-db")
    CELERY_BROKER_URL = values.Value()


class Prod(Dev): # settings for production
    DEBUG = values.BooleanValue(False)
    SECRET_KEY = values.SecretValue() # read from environment variable only
    ALLOWED_HOSTS = values.ListValue(["localhost", "0.0.0.0", "sg-attractions-outings.up.railway.app"]) # read from environment variable string