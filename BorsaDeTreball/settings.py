"""
Django settings for BorsaDeTreball project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

from BorsaDeTreball import settings2


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOSITORY_ROOT = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings2.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings2.DEBUG

ALLOWED_HOSTS = settings2.ALLOWED_HOSTS

SESSION_COOKIE_AGE = 4 * 60 * 60 # les sessions duren 4 hores per defecte

# Application definition

INSTALLED_APPS = [
    # plugins
    #'BorsaDeTreball.apps.MyAdminConfig', 
    #'test_without_migrations',
    'easy_select2',
    'djrichtextfield',
    'social_django',
    'adminsortable2',
    'django_select2',
    'django_admin_select2',
    # django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    # apps
    'core',
    'borsApp',
    'scrum',
]
# OAuth -> 
AUTHENTICATION_BACKENDS = (
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOpenId',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.google.GoogleOAuth',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    #'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    #'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'BorsaDeTreball.urls'
# OAuth
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]


WSGI_APPLICATION = 'BorsaDeTreball.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    #'sqlite': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #},
    'mysql': { # mysql
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        #'ENGINE': 'django.db.backends.mysql',
        #'ENGINE': 'mysql.connector.django', # MySQL 8 (problemes amb GIS)
        'NAME': settings2.DB_NAME,
        'USER': settings2.DB_USER,
        'PASSWORD': settings2.DB_PASS,
        'HOST': settings2.DB_HOST or "localhost",
        'PORT': settings2.DB_PORT or 3306,
    },
    'postgre': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': settings2.DB_NAME,
        'USER': 'user001',
        'PASSWORD': '123456789',
        'HOST': settings2.DB_HOST or 'localhost',
        'PORT': settings2.DB_PORT or 5432,
    },
}

DATABASES["default"] = DATABASES[settings2.DB_TYPE]

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'core.User'


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'ca-ES'
#TIME_ZONE = 'UTC'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_L10N = True
USE_TZ = True

from django.conf.locale.ca import formats as ca_formats
ca_formats.DATETIME_FORMAT = "d M Y H:i:s"


DJRICHTEXTFIELD_CONFIG = {
    'js': ['//tinymce.cachefly.net/4.1/tinymce.min.js'],
    'init_template': 'djrichtextfield/init/tinymce.js',
    'settings': {
        'menubar': False,
        'plugins': 'link image autoresize code',
        'toolbar': 'bold italic | link image | removeformat code',
        'width': 700,
        #'statusbar': False,
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_URL = '/media/'


EMAIL_HOST = settings2.EMAIL_HOST
EMAIL_PORT = settings2.EMAIL_PORT
EMAIL_FROM_NAME = settings2.EMAIL_FROM_NAME
EMAIL_HOST_USER = settings2.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings2.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = settings2.EMAIL_USE_TLS
EMAIL_USE_SSL = settings2.EMAIL_USE_SSL


SOCIAL_AUTH_URL_NAMESPACE = settings2.SOCIAL_AUTH_URL_NAMESPACE
SOCIAL_AUTH_LOGIN_REDIRECT_URL = settings2.SOCIAL_AUTH_LOGIN_REDIRECT_URL
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY =  settings2.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = settings2.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET
# Microsoft no present en aquest plugin
#SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY =  settings2.SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY
#SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET = settings2.SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET


#no fem servir aquest plugin
#SOCIAL_AUTH_WHITELISTED_EMAILS = ['enric.mieza@gmail.com',]


# Ajustos per accelerar testing
#TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

# enviament maxim d'emails
MAX_EMAILS = 3


