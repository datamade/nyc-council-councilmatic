import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'la testa degli italiani'

# SECURITY WARNING: don't run with debug turned on in production!
# Set this to True while you are developing
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'travis',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/nyc-council-councilmatic',
    },
}

# Remember to run python manage.py createcachetable so this will work! 
# developers, set your BACKEND to 'django.core.cache.backends.dummy.DummyCache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'councilmatic_cache',
    }
}

# Set this to flush the cache at /flush-cache/{FLUSH_KEY}
FLUSH_KEY = 'flushitallaway'

ANALYTICS_TRACKING_CODE = ''

HEADSHOT_PATH = os.path.join(os.path.dirname(__file__), '..'
                             '/nyc/static/images/')

RQ_QUEUES = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
        'DB': 1,
        'PASSWORD': '',
        'DEFAULT_TIMEOUT': 360,
    }
}

#RQ_EXCEPTION_HANDLERS = ['path.to.my.handler'] # If you need custom exception handlers
RQ_SHOW_ADMIN_LINK = True

EMAIL_HOST='smtp.example.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='user'
EMAIL_HOST_PASSWORD='password'
DEFAULT_FROM_EMAIL='NYC Councilmatic <info@councilmatic.org>'

TIME_ZONE = 'US/Eastern'
