# app lives in a directory above our example
# project so we need to make sure it is findable on our path.
import sys
import os
from os.path import abspath, dirname, join
parent = abspath(dirname(__file__))
grandparent = abspath(join(parent, '..'))
for path in (grandparent, parent):
    if path not in sys.path:
        sys.path.insert(0, path)

DEBUG = True
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': abspath(join(parent, 'example.db')),
    }
}

SECRET_KEY = 'x'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
ADMIN_MEDIA_PREFIX = '/static/admin/'

ROOT_URLCONF = 'urls'

PROJECT_APPS = ('djadmin_ext', 'sample')

INSTALLED_APPS = (
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles', 'django_nose'
) + PROJECT_APPS

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [abspath(join(parent, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug':
            DEBUG,
        },
    },
]

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

FIXTURE_DIRS = [
    'example/sample/fixtures/',
]
