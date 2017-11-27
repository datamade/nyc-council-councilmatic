import pytest

from django.core.urlresolvers import reverse

from councilmatic_core.models import Event
from nyc.utils import create_ics_output, create_google_cal_link
  
@pytest.mark.django_db
def test_ics_output():
    event = Event.objects.all().first()
    ics_content = create_ics_output(event).decode("utf-8")

    # The content should include the event name.
    assert (event.name in ics_content) == True 

@pytest.mark.django_db
def test_ical_export(django_db_setup, client):
    event = Event.objects.all().first()
    url = reverse('nyc:ical_export', kwargs={'slug': event.slug})
    response = client.get(url) 

    # The response should return a 200, present a content type of 'text/calendar', and contain an attachment with the slug as its file name.
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/calendar'
    assert response['Content-Disposition'] == 'attachment; filename={}.ics'.format(event.slug)

@pytest.mark.django_db
def test_create_google_cal_link(django_db_setup):
    event = Event.objects.all().first()
    cal_url = create_google_cal_link(event)

    # The output of create_google_cal_link should contain particular substrings. 
    assert (event.name.strip().replace(' ', '+') in cal_url) == True
    assert (event.start_time.strftime('%Y%m%dT%H%M%SZ') in cal_url) == True
    assert (event.location_name.strip().replace(' ', '+') in cal_url) == True