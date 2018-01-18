import datetime
import pytz

from uuid import uuid4
import pytest
from django.test import TestCase
from django.conf import settings

from nyc.models import NYCBill
from councilmatic_core.models import Action

class TestStatus(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Make some bills for testing.
        '''
        super().setUpClass()

        cls.active_bill = NYCBill.objects.create(
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

        cls.inactive_bill = NYCBill.objects.create(
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

        cls.expired_bill = NYCBill.objects.create(
            ocd_id = 'ocd-bill/' + str(uuid4()),
            ocd_created_at = datetime.datetime.now(pytz.utc),
            ocd_updated_at = datetime.datetime.now(pytz.utc),
            description = 'Expired bill for testing',
            identifier = 'T 2018-03',
            bill_type = 'Test bill',
            classification = 'bill',
            source_url = '127.0.0.1:8000',
            slug = 'expired-bill'
        )

        cls.failed_bill = NYCBill.objects.create(
            ocd_id = 'ocd-bill/' + str(uuid4()),
            ocd_created_at = datetime.datetime.now(pytz.utc),
            ocd_updated_at = datetime.datetime.now(pytz.utc),
            description = 'Failed bill for testing',
            identifier = 'T 2018-03',
            bill_type = 'Test bill',
            classification = 'bill',
            source_url = '127.0.0.1:8000',
            slug = 'failed-bill'
        )

        cls.active_action = Action.objects.create(
            date = datetime.datetime.now(pytz.utc),
            _bill = cls.active_bill,
            order = 1,
        )

        cls.inactive_action = Action.objects.create(
            date = datetime.datetime.now() - datetime.timedelta(151),
            _bill = cls.inactive_bill,
            order = 1,
        )

        cls.expired_action = Action.objects.create(
            classification = 'failure',
            description = 'Filed (End of Session)',
            date = datetime.datetime.now(pytz.utc),
            _bill = cls.expired_bill,
            order = 1,
        )

        cls.failed_action = Action.objects.create(
            classification = 'failure',
            description = 'Defeated by Council',
            date = settings.ACTIVE_SESSION - datetime.timedelta(1),
            _bill = cls.failed_bill,
            order = 1,
        )

    @pytest.mark.django_db
    def test_active_bill(self):
        assert self.active_bill.inferred_status == 'Active'

    @pytest.mark.django_db
    def test_inactive_bill(self):
        assert self.inactive_bill.inferred_status == 'Inactive'

    @pytest.mark.django_db
    def test_expired_bill(self):
        assert self.expired_bill.inferred_status == 'Expired'

    @pytest.mark.django_db
    def test_failed_bill(self):
        assert self.failed_bill.inferred_status == 'Failed'

