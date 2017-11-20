import pytest

from django.core.urlresolvers import reverse

from councilmatic_core.models import Event
from nyc.utils import create_ics_output
  
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
def test_google_calendar_export(django_db_setup, client):
    event = Event.objects.all().first()
    url = reverse('nyc:google_calendar_export', kwargs={'slug': event.slug})
    response = client.get(url) 

    # The response should redirect.
    assert response.status_code == 302