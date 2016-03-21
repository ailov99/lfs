"""
Django settings for lfs_project project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
#from lfs.models import Teacher


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/img')


# template directory path
TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates')

# template directory



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(j*l-k*=c400^r-^2ns6-&#1g(jbj#mf2+zx&6#z&s7q))=a*h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'lfs',
    'lfs_forum',
    'lfs_admin',
    'lfs_quiz',
    'bootstrapform',
    'hitcount',
    'passwords',
    'precise_bbcode',
    'pybb',
]

TEMPLATE_DIRS = [TEMPLATE_PATH]

MIDDLEWARE_CLASSES = [
    #'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pybb.middleware.PybbMiddleware',
]

ROOT_URLCONF = 'lfs_project.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth',
    #'django.contrib.messages.context_processors.messages',
    'pybb.context_processors.processor',
)

#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [TEMPLATE_PATH],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]

WSGI_APPLICATION = 'lfs_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PROFILE_MODULE = 'lfs.models.Teacher'

#AUTH_PASSWORD_VALIDATORS = [
#    {
#        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#    },
#    {
#        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#    },
#]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

SITE_ID = 1

STATIC_PATH = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    STATIC_PATH,
)

MEDIA_URL = '/static/img/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static/img')

# PYBB forum settings
#PYBB_PROFILE_RELATED_NAME = Teacher
PYBB_DEFAULT_TITLE = 'LFS Forum'
PYBB_SMILES_PREFIX = 'pybb/emoticons/'

# Login Redirects

LOGIN_URL = '/lfs/login/'
LOGIN_REDIRECT_URL = '/lfs/'

# Hitcount app
HITCOUNT_KEEP_HIT_ACTIVE = {'days': 1 }
HITCOUNT_KEEP_HIT_IN_DATABASE = { 'days': 8 }

# Enforce password strength
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY = { "UPPER":  1, "LOWER":  1, "DIGITS": 1 }
