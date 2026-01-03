"""Simple Django settings for tests."""

SECRET_KEY = 'test-secret-key-for-testing-purposes-only'

INSTALLED_APPS = [
    'django_admin_advanced_search',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

USE_TZ = True