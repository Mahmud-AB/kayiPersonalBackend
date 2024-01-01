import os

import environ
import paypalrestsdk
import sys

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
environ.Env.read_env()
env_file = os.path.join(BASE_DIR, 'config', ".env." + "development")
# print("Env: " + env('ENV_TYPE'))
environ.Env.read_env(env_file=env_file, overwrite=True)

SECRET_KEY = env('SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_swagger',
    'oauth2_provider',
    'rest_framework',
    'web_api',
    'web_view',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'config.middleware.AdminSellerMiddleware',
    'config.middleware.AuditMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
)

OAUTH2_PROVIDER = {
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600 * 24 * 7,
    'OAUTH_DELETE_EXPIRED': True
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["web_view/template"],
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
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}
WSGI_APPLICATION = 'config.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': env('DATABASE_NAME'),
#         'USER': env('DATABASE_USER'),
#         'PASSWORD': env('DATABASE_PASS'),
#         'HOST': env('DATABASE_HOST'),
#         'PORT': 3306,
#         'STORAGE_ENGINE': 'MyISAM / INNODB / ETC'
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'] if 'DB_ENGINE' in os.environ else 'django.db.backends.sqlite3',
        'NAME': os.environ['DB_NAME'] if 'DB_NAME' in os.environ else BASE_DIR / 'db.sqlite3',
        'USER': os.environ['DB_USER'] if 'DB_NAME' in os.environ else '',
        'PASSWORD': os.environ['DB_PASSWORD'] if 'DB_PASSWORD' in os.environ else '',
        'HOST': os.environ['DB_HOST'] if 'DB_HOST' in os.environ else '',  
        # 'HOST': '208-109-36-15',   # Or an IP Address that your DB is hosted on
        'PORT': os.environ['DB_PORT'] if 'DB_PORT' in os.environ else '',
    }
}
if 'MYSQL' in os.environ and os.environ['MYSQL']==1:
    DATABASES['default']['OPTIONS'] = {
        'sql_mode':'traditional'
    }

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

SESSION_COOKIE_SECURE = False
ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = "web_api.Users"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Dhaka'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'nirbanmitra007@gmail.com'
EMAIL_HOST_PASSWORD = 'lsyz hlle sggs cghm'

EMAIL_HOST_USER_SUPPORT = 'info@kayi.us'
EMAIL_HOST_PASSWORD_SUPPORT = 'Falcon098@'

EMAIL_USE_TLS = True

PAYPAL_MODE = env('PAYPAL_MODE')
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = env('PAYPAL_CLIENT_SECRET')

AWS_STORAGE_KEY_ID = "AKIASGCZXQOSZURABOLA"
AWS_STORAGE_KEY_TOKEN = "906xrZAHfuBiSkOi449IK3h8x56LYnJ7AeNcj7lS"
AWS_STORAGE_BUCKET_NAME = "thekayi"

STATIC_URL = '/public/'
STATIC_FILE_PATH = os.path.join(BASE_DIR, "web_view/global")
if DEBUG:
    STATICFILES_DIRS = [STATIC_FILE_PATH]
else:
    STATIC_ROOT = STATIC_FILE_PATH
