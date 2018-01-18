import unittest
import datetime
import pytz

from uuid import uuid4

from councilmatic_core.models import Bill


class TestBillStatus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Make some bills for testing.
        '''
        cls.active_bill = Bill.objects.create(
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

        cls.inactive_bill = Bill.objects.create(
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

        cls.filed_bill = Bill.objects.create(
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

    def test_inactive(self):
        pass
