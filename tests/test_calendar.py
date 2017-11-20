import pytest

from django.core.urlresolvers import reverse

from councilmatic_core.models import Event
    
@pytest.mark.django_db
def test_ical_export(django_db_setup, client):
    event = Event.objects.get(ocd_id='ocd-event/02481351-47b5-46c5-9401-b7ad1fc49a0b')
    url = reverse('nyc:ical_export', kwargs={'slug': event.slug})
    response = client.get(url) 

    # The response should return a 200, present a content type of 'text/calendar', and contain an attachment with the slug as its file name.
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/calendar'
    assert response['Content-Disposition'] == 'attachment; filename={}.ics'.format(event.slug)
