import os
from datetime import timedelta
from os.path import join
import environ
from distutils.util import strtobool
import dj_database_url
from configurations import Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
base = environ.Path(__file__) - 3  # Two folders back -> root of project
# reading .env file
try:
    environ.Env.read_env(env_file=base('.env'))
except FileNotFoundError:
    pass  # Log here!


class Common(Configuration):
    # Celery Configuration Options
    CELERY_BROKER_TRANSPORT = 'redis'
    CELERY_BROKER_URL = env('CELERY_REDIS_URL')
    CELERY_RESULT_BACKEND = env('CELERY_REDIS_URL')
    CELERY_TIMEZONE = "America/Argentina/Cordoba"
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60

    INSTALLED_APPS = (
        'material.admin',
        'material.admin.default',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.gis',


        # Third party apps
        'corsheaders',
        'channels',
        'rest_framework',            # utilities for rest apis
        'rest_framework_gis',
        'rest_framework.authtoken',  # token authentication
        'django_filters',            # for filtering rest endpoints
        'encrypted_fields',
        'simple_history',
        "fcm_django",
        "django_celery_beat",

        # Your apps
        'sicoin.users',
        'sicoin.domain_config',
        'sicoin.incident',
        'sicoin.geolocation',
        'sicoin.wsdebug',
        'chat',
        'drf_yasg',

    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'simple_history.middleware.HistoryRequestMiddleware',
    )

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # TODO: localhost must not be present on production builds
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", ".herokuapp.com"]
    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost",
        "https://tesis-cabal-cugno-moreyra.onrender.com",
    ]
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^https://tesis-cabal-cugno-moreyra-pr-\d+\.onrender\.com$",
        r"^http://192\.168\.\d+\.\d+:808[01]$",
    ]
    ROOT_URLCONF = 'sicoin.urls'
    SECRET_KEY = env('DJANGO_SECRET_KEY')
    FIELD_ENCRYPTION_KEYS = [env('FIELD_ENCRYPTION_KEY')]
    WSGI_APPLICATION = 'sicoin.wsgi.application'
    ASGI_APPLICATION = "sicoin.routing.application"
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [env('REDIS_URL')],
            },
        },
    }

    FCM_DJANGO_SETTINGS = {
        "FCM_SERVER_KEY": env('FCM_API_KEY'),
        "ONE_DEVICE_PER_USER": True,
    }

    # Email
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    ADMINS = (
        ('Author', 'tesis.cabal.cugno.moreyra@gmail.com '),
    )

    # Postgres
    DATABASES = {
        'default': dj_database_url.config(
            default=env('POSTGRES_CONN', default='postgresql://root:password@postgres:5432/db_dev'),
            conn_max_age=int(env('POSTGRES_CONN_MAX_AGE', default=600)),
            engine='django.contrib.gis.db.backends.postgis'
        )
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = []
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': STATICFILES_DIRS,
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

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(env('DJANGO_DEBUG', default='no'))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
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

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
            'daphne': {
                'handlers': [
                    'console',
                ],
                'propagate': True,
                'level': 'DEBUG'
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(env('DJANGO_PAGINATION_LIMIT', default=10)),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        )
    }

    REST_USE_JWT = True

    REST_AUTH_SERIALIZERS = {
        'JWT_TOKEN_CLAIMS_SERIALIZER': 'sicoin.users.serializers.CustomTokenObtainPairSerializer',
        'USER_DETAILS_SERIALIZER': 'sicoin.users.serializers.UserDetailsAfterLoginSerializer'
    }

    JWT_AUTH_COOKIE = 'jwt-auth'

    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ROTATE_REFRESH_TOKENS': False,
        'BLACKLIST_AFTER_ROTATION': True,
        'UPDATE_LAST_LOGIN': False,

        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'VERIFYING_KEY': None,
        'AUDIENCE': None,
        'ISSUER': None,
    }

    SWAGGER_SETTINGS = {
        'SECURITY_DEFINITIONS': {
            'Basic': {
                'type': 'basic'
            },
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'schemeName': 'Bearer'
            }
        },
        'DEFAULT_API_URL': env('DEFAULT_API_URL', default=None)
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env('REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": env('REDIS_PASSWD')
            }
        }
    }

    INCIDENT_WS_DATA_GENERATION = False

    MATERIAL_ADMIN_SITE = {
        'HEADER': 'SICOIN Internal Administration',  # Admin site header
        'TITLE': 'SICOIN Internal Administration',  # Admin site title
        'MAIN_BG_COLOR': 'black',  # Admin site main color, css color should be specified
        'MAIN_HOVER_COLOR': 'blue',  # Admin site main hover color, css color should be specified
        # 'PROFILE_PICTURE': 'path/to/image',  # Admin site profile picture
        # 'PROFILE_BG': 'path/to/image',  # Admin site profile background
        # 'LOGIN_LOGO': 'path/to/image',  # Admin site logo on login page
        # 'LOGOUT_BG': 'path/to/image',
        # Admin site background on login/logout pages (path to static should be specified)
        'SHOW_THEMES': True,  # Show default admin themes button
        # 'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
        'SHOW_COUNTS': True,  # Show instances counts for each model
        # 'APP_ICONS': {
        #     # Set icons for applications(lowercase), including 3rd party apps,
        #     {'application_name': 'material_icon_name', ...}
        #     'sites': 'send',
        # },
        # 'MODEL_ICONS': {
        #     # Set icons for models(lowercase), including 3rd party models,
        #     {'model_name': 'material_icon_name', ...}
        #     'site': 'contact_mail',
        # }
    }
