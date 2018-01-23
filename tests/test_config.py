SECRET_KEY = 'riva loves cuzzoni'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'haystack',
    'nyc',
    'councilmatic_core',
    'notifications',
    'django_rq',
    'password_reset',
    'adv_cache_tag',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

CITY_NAME = 'New York City'
CITY_NAME_SHORT = 'NYC'
CITY_COUNCIL_NAME = 'New York City Council'
OCD_JURISDICTION_ID = 'ocd-jurisdiction/country:us/state:ny/place:new_york/government'
OCD_CITY_COUNCIL_ID = 'ocd-organization/0f63aae8-16fd-4d3c-b525-00747a482cf9'

APP_NAME = 'nyc'

STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'councilmatic_core.views.city_context'
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_nyc',
        'USER': '',
        'PASSWORD': '',
        'PORT': 5432,
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr',
    },
}

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 1,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    }
}

USING_NOTIFICATIONS = True

ROOT_URLCONF = 'councilmatic.urls'

TIME_ZONE = 'US/Eastern'

USE_TZ = True
