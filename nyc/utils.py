from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from icalendar import Calendar, Event

from django.conf import settings 

from datetime import datetime, timedelta

try:
    import argparse
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

# Helper function for exporting events to Google calendar.
def get_credentials():
    """Gets valid user credentials from storage.
    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)

    return credentials

# Helper function for exporting events to Google calendar.
def export_event(event):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    event_google = {
      'summary': event.name,
      'location': event.location_name,
      'description': event.description,
      'start': {
        'dateTime': event.start_time.isoformat(),
        'timeZone': settings.TIME_ZONE,
      },
      'end': {
        'dateTime': (event.start_time + timedelta(hours=2)).isoformat(),
        'timeZone': settings.TIME_ZONE,
      },
    }

    service.events().insert(calendarId='primary', body=event_google).execute()

# Helper function for creating a ICS file.
def create_ics_output(event):
    cal = Calendar()
    event_ics = Event()
    output = ''

    event_ics.add('summary', event.name)
    event_ics.add('location', event.location_name)
    event_ics.add('description', event.description)
    event_ics.add('dtstart', event.start_time)
    event_ics.add('dtend', (event.start_time + timedelta(hours=2)))

    cal.add_component(event_ics)

    for line in cal.content_lines():
      if line:
        output += line + "\n"
    
    return output
