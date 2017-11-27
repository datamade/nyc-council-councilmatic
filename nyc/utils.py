from icalendar import Calendar, Event

from django.conf import settings 

from datetime import datetime, timedelta


def create_google_cal_link(event):
    time_fmt = '%Y%m%dT%H%M%SZ'

    event_url = ('https://www.google.com/calendar/render?action=TEMPLATE&text={text}'
        '&dates={start_time}/{end_time}'
        '&details={details}'
        '&location={location}'
        '&sf=true&output=xml').format(text=event.name.strip(),
                start_time=event.start_time.strftime(time_fmt),
                end_time=(event.start_time + timedelta(hours=2)).strftime(time_fmt),
                details=event.description.strip(),
                location=event.location_name.strip())


    return event_url.replace(' ', '+')


def create_ics_output(event):
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '-//NYC Councilmatic//nyc.councilmatic.org//EN')
    cal.add('x-wr-timezone', "US/Eastern")
    cal.add('method', 'publish')

    event_ics = Event()
    event_ics.add('summary', event.name)
    event_ics.add('location', event.location_name)
    event_ics.add('description', event.description)
    event_ics.add('dtstart', event.start_time)
    event_ics.add('dtend', (event.start_time + timedelta(hours=2)))
    event_ics.add('dtstamp', event.start_time)
    event_ics.add('uid', event.ocd_id)

    cal.add_component(event_ics)
    
    return cal.to_ical()

