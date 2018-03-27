from django.shortcuts import render
from django.http import HttpResponsePermanentRedirect, HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction, connection, connections

from datetime import date, timedelta
import re
from collections import namedtuple

from .utils import create_google_cal_link, create_ics_output

from nyc.models import NYCBill

from councilmatic_core.models import Event, Organization, Bill
from councilmatic_core.views import *
from haystack.query import SearchQuerySet


class NYCIndexView(IndexView):
    template_name = 'nyc/index.html'
    bill_model = NYCBill

class NYCAboutView(AboutView):
    template_name = 'nyc/about.html'

class NYCBillDetailView(BillDetailView):
    model = NYCBill

    def dispatch(self, request, *args, **kwargs):
        '''
        NYC Councilmatic requires several redirects, due to the historic nature of the app.
        The slugs may exist in several older forms:
        (1) a mangled form: missing a leading zero, e.g., int-262-2018 (old slug) vs. int-0262-2018
        (2) a mangled form: an added space, e.g.,  t-2015-3713 (old slug) vs. t-2015-3713
        (3) a shortened form, e.g., res-190 (old slug) 
        (4) a slug extended with a UUID, e.g., int-262-2018-060ed381 (old slug)
        '''
        slug = self.kwargs['slug']

        try:
            bill = self.model.objects.get(slug=slug)
            response = super().dispatch(request, *args, **kwargs)
        except NYCBill.DoesNotExist:
            bill = None

        # Redirects
        if bill is None:
            # Cases 1 and 4
            deleted_zeroes = r'^((?!t-)[A-Za-z]+)-(\d{1,3})-([-\d]+)$'
            match_deleted_zeroes = re.match(deleted_zeroes, slug)
            if match_deleted_zeroes:
                prefix = match.group(1)
                digits_before_hyphen = match.group(2)
                remainder = match.group(3).split('-')[0]
                repaired_slug = '{prefix}-{digits_before_hyphen:0>4}-{remainder}'.format(prefix=prefix, digits_before_hyphen=digits_before_hyphen, remainder=remainder)
            
            # Case 2
            added_space = r'^(t)-([-\d]+)$'
            match_added_space = re.match(added_space, slug)
            if match_added_space:
                repaired_slug = '{prefix}{remainder}'.format(prefix=prefix, remainder=remainder)
        
            try:
                bill = self.model.objects.get(slug=repaired_slug)
            except NYCBill.DoesNotExist:
                # Case 3
                bill = self.model.objects.get(slug__startswith=slug)
                response = HttpResponsePermanentRedirect(reverse('bill_detail', args=[bill.slug]))

            # # Case 1 and 4
            # try:
            #     # Old slugs: res-190-2018, res-190-2018-3489283409184098
            #     # New slug: res-0190-2018
            #     prefix, digits_before_hyphen, *remainder = slug.split('-')
            #     remainder = remainder[0] if remainder else ''
            #     repaired_slug = '{prefix}-{digits_before_hyphen:0>4}-{remainder}'.format(prefix=prefix, digits_before_hyphen=digits_before_hyphen, remainder=remainder)
            #     bill = self.model.objects.get(slug=repaired_slug)
            #     response = HttpResponsePermanentRedirect(reverse('bill_detail', args=[bill.slug]))
            # except NYCBill.DoesNotExist:
            #     # Case 3
            #     try:
            #         bill = self.model.objects.get(slug__startswith=slug)
            #         response = HttpResponsePermanentRedirect(reverse('bill_detail', args=[bill.slug]))
            #     except NYCBill.DoesNotExist:
            #         try: 
            #             # Old slug: t-2015-3716
            #             # New slug: t2015-3716
            #             bill = self.model.objects.get(slug=slug.replace('-', ''))




            # try:
            #     bill = self.model.objects.get(slug__startswith=slug)
            #     response = HttpResponsePermanentRedirect(reverse('bill_detail', args=[bill.slug]))
            # except NYCBill.DoesNotExist:
            #     try: 
            #         one, two, three, four = slug.split('-')
            #         short_slug = slug.replace('-' + four, '')
            #         bill = self.model.objects.get(slug__startswith=short_slug)
            #         response = HttpResponsePermanentRedirect(reverse('bill_detail', args=[bill.slug]))
            #     except:
            #         response = HttpResponseNotFound()

        # Are these code redirects even used? how can we know? 

        return response

class NYCCommitteeDetailView(CommitteeDetailView):
    model = Organization

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs['slug']

        try:
            committee = self.model.objects.get(slug=slug)
            response = super().dispatch(request, *args, **kwargs)
        except Organization.DoesNotExist:
            committee = None

        if committee is None:
            try:
                slug = slug.replace(',', '').replace('\'', '')
                committee = self.model.objects.get(slug__startswith=slug)
                response = HttpResponsePermanentRedirect(reverse('committee_detail', args=[committee.slug]))
            except Organization.DoesNotExist:
                response = HttpResponseNotFound()

        return response

class NYCPersonDetailView(PersonDetailView):
    model = Person

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs['slug']

        try:
            person = self.model.objects.get(slug=slug)
            response = super().dispatch(request, *args, **kwargs)
        except Person.DoesNotExist:
            person = None

        if person is None:
            person_name = slug.replace('-', ' ')
            try:
                slug = slug.replace(',', '').replace('\'', '').replace('--', '-')
                person = self.model.objects.get(slug__startswith=slug)
                response = HttpResponsePermanentRedirect(reverse('person', args=[person.slug]))

            except Person.MultipleObjectsReturned:
                person_name = slug.replace('-', ' ').replace('.', '')
                # If duplicate person has middle initial.
                if re.match(r'\w+[\s.-]\w+[\s.-]\w+', slug) is not None:
                    person_name = re.sub(r'(\w+\s\w+)(\s\w+)', r'\1.\2', person_name)
                person = self.model.objects.get(name__iexact=person_name)
                response = HttpResponsePermanentRedirect(reverse('person', args=[person.slug]))
            except Person.DoesNotExist:
                response = HttpResponseNotFound()

        return response

class NYCBillWidgetView(BillWidgetView):
    model = NYCBill

class NYCCommitteesView(CommitteesView):

    def get_queryset(self):
        return []

    def get_context_data(self, **kwargs):
        context = super(CommitteesView, self).get_context_data(**kwargs)

        committees = Organization.committees().filter(name__startswith='Committee')

        context['committees'] = [c for c in committees if c.memberships.all()]

        subcommittees = Organization.committees().filter(name__startswith='Subcommittee')
        context['subcommittees'] = [c for c in subcommittees if c.memberships.all()]

        taskforces = Organization.committees().filter(name__startswith='Task Force')
        context['taskforces'] = [c for c in taskforces if c.memberships.all()]

        return context

class NYCEventDetailView(EventDetailView):
    template_name = 'nyc/event.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = context['event']

        event_url = create_google_cal_link(event)
        context['event_url'] = event_url

        # Logic for getting relevant board report information.
        with connection.cursor() as cursor:
            query = '''
                SELECT distinct
                    b.identifier,
                    b.slug,
                    b.description,
                    i.order
                FROM councilmatic_core_bill AS b
                INNER JOIN councilmatic_core_eventagendaitem as i
                ON i.bill_id=b.ocd_id
                WHERE i.event_id='{}'
                GROUP BY
                    b.identifier,
                    b.slug,
                    b.description,
                    i.order 
                ORDER BY i.order
                '''.format(event.ocd_id)

            cursor.execute(query)

            # Get field names
            columns = [c[0] for c in cursor.description]
        
            # Create a named tuple
            bill_tuple = namedtuple('BillProperties', columns, rename=True)
            # Put results inside a list with assigned fields (from namedtuple)
            related_bills = [bill_tuple(*r) for r in cursor]

            context['related_bills'] = related_bills

        return context

# Views for calendar exports.
def ical_export(request, slug):
    event = Event.objects.get(slug=slug)
    output = create_ics_output(event)
  
    response = HttpResponse(output, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename={}.ics'.format(event.slug) 

    return response

class NYCCouncilmaticFacetedSearchView(CouncilmaticFacetedSearchView):

    def build_form(self, form_kwargs=None):
        form = super(CouncilmaticFacetedSearchView, self).build_form(form_kwargs=form_kwargs)

        # For faceted search functionality.
        if form_kwargs is None:
            form_kwargs = {}

        form_kwargs['selected_facets'] = self.request.GET.getlist("selected_facets")

        # For remaining search functionality.
        data = None
        kwargs = {
            'load_all': self.load_all,
        }

        sqs = SearchQuerySet().facet('bill_type')\
                      .facet('sponsorships', sort='index', limit=-1)\
                      .facet('controlling_body')\
                      .facet('inferred_status')\
                      .facet('legislative_session', sort='index')\
                      .highlight()

        if form_kwargs:
            kwargs.update(form_kwargs)

        dataDict = {}
        if len(self.request.GET):
            data = self.request.GET
            dataDict = dict(data)

        if self.searchqueryset is not None:
            kwargs['searchqueryset'] = sqs

            if dataDict.get('sort_by'):
                for el in dataDict['sort_by']:
                    # Do this, because sometimes the 'el' may include a '?' from the URL
                    if 'date' in el:
                        if dataDict.get('ascending'):
                            kwargs['searchqueryset'] = sqs.order_by('last_action_date')
                        else:
                            kwargs['searchqueryset'] = sqs.order_by('-last_action_date')
                    if 'title' in el:
                        if dataDict.get('descending'):
                            kwargs['searchqueryset'] = sqs.order_by('-sort_name')
                        else:
                            kwargs['searchqueryset'] = sqs.order_by('sort_name')
                    if 'relevance' in el:
                        kwargs['searchqueryset'] = sqs

            elif dataDict.get('q'):
                kwargs['searchqueryset'] = sqs
            else:
                kwargs['searchqueryset'] = sqs.order_by('-last_action_date')

        return self.form_class(data, **kwargs)
