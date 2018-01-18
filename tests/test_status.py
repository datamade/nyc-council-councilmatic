import datetime
import pytz

from uuid import uuid4
import pytest

from councilmatic_core.models import Bill, Action

@pytest.fixture(scope='module')
def bills():
    '''
    Make some bills for testing.
    '''
    active_bill = Bill(
        ocd_id = 'ocd-bill/' + str(uuid4()),
        ocd_created_at = datetime.datetime.now(pytz.utc),
        ocd_updated_at = datetime.datetime.now(pytz.utc),
        description = 'Active bill for testing',
        identifier = 'T 2018-01',
        bill_type = 'Test bill',
        classification = 'bill',
        source_url = '127.0.0.1:8000',
        slug = 'active-bill'
    )

    inactive_bill = Bill(
        ocd_id = 'ocd-bill/' + str(uuid4()),
        ocd_created_at = datetime.datetime.now(pytz.utc),
        ocd_updated_at = datetime.datetime.now(pytz.utc),
        description = 'Inactive bill for testing',
        identifier = 'T 2018-02',
        bill_type = 'Test bill',
        classification = 'bill',
        source_url = '127.0.0.1:8000',
        slug = 'inactive-bill'
    )

    filed_bill = Bill(
        ocd_id = 'ocd-bill/' + str(uuid4()),
        ocd_created_at = datetime.datetime.now(pytz.utc),
        ocd_updated_at = datetime.datetime.now(pytz.utc),
        description = 'Filed bill for testing',
        identifier = 'T 2018-03',
        bill_type = 'Test bill',
        classification = 'bill',
        source_url = '127.0.0.1:8000',
        slug = 'filed-bill'
    )

    active_action = Action(
        date = datetime.datetime.now(pytz.utc),
        classification = None,
        _organization = None,
        _bill = active_bill,
        order = 1,
    )

    yield {
        'active_bill': active_bill,
        'inactive_bill': inactive_bill,
        'filed_bill': filed_bill,
        'active_action': active_action
    }

@pytest.mark.django_db
def test_inactive(bills):
    import pdb
    pdb.set_trace()
