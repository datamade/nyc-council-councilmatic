import pytest
import pytz
import datetime

from django.core.management import call_command
from django.utils.timezone import make_aware
from django.conf import settings

from councilmatic_core.models import Bill, Event

app_timezone = pytz.timezone(settings.TIME_ZONE)

@pytest.fixture
@pytest.mark.django_db
def bill(db):
    class BillFactory():
        def build(self, **kwargs):
            timestamp = datetime.datetime(2017, 6, 9, 13)

            bill_info = {
                'ocd_id': 'ocd-bill/060ed381-a2d7-43ea-a746-46fd84ebfff5',
                'description': 'Proposed legislation amend a law',
                'ocd_created_at': make_aware(timestamp, app_timezone),
                'ocd_updated_at': make_aware(timestamp, app_timezone),
                'updated_at': make_aware(timestamp, app_timezone),
                'identifier': 'Int 0262-2018',
                'slug': 'int-0262-2018'
            }

            bill_info.update(kwargs)

            bill = Bill.objects.create(**bill_info)
            bill.save()

            return bill

    return BillFactory()

@pytest.fixture
@pytest.mark.django_db
def event(db):
    class EventFactory():
        def build(self, **kwargs):
            timestamp = datetime.datetime(2017, 5, 17, 11, 6)
            start_time = datetime.datetime(2017, 9, 27, 12, 30)

            event_info = {
                "ocd_id": "ocd-event/02481351-47b5-46c5-9401-b7ad1fc49a0b",
                "ocd_created_at": "2017-05-27 11:10:46.574-05", 
                "ocd_updated_at": "2017-05-27 11:10:46.574-05", 
                "name": "City Council Stated Meeting",
                "location_name": "Council Chambers, City Hall",
                "description": "",
                "start_time": make_aware(start_time, app_timezone),
                "updated_at": make_aware(timestamp, app_timezone),
                "slug": "city-council-stated-meeting-b7ad1fc49a0b"
            }

            event_info.update(kwargs)

            event = Event.objects.create(**event_info)
            event.save()

            return event

    return EventFactory()