import pytest

from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    '''Insert test_data.json into the `test_nyc` database
    '''
    with django_db_blocker.unblock():
        call_command('loaddata', 'tests/test_data.json')