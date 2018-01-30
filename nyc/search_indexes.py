from haystack import indexes

from django.conf import settings

from datetime import datetime, timedelta
import pytz

from nyc.models import NYCBill
from councilmatic_core.haystack_indexes import BillIndex
from councilmatic_core.models import Action

app_timezone = pytz.timezone(settings.TIME_ZONE)


class NYCBillIndex(BillIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True,
                             template_name="search/indexes/nyc/bill_text.txt")

    def get_model(self):
        return NYCBill

    def index_queryset(self, using=None):
        # excluding NYC bill types that are not really legislation
        invalid_bill_types = ['Town Hall Meeting', 'Oversight', 'Tour', 'Local Laws 2015']
        return self.get_model().objects.exclude(bill_type__in=invalid_bill_types)

    def prepare_last_action_date(self, obj):
        app_timezone = pytz.timezone(settings.TIME_ZONE)

        if not obj.last_action_date:
            index_actions = [a.date for a in obj.actions.all()]

            if index_actions:
                # Newer versions of Solr seem to be fussy about the time format, and we do not need the time, just the date stamp.
                # https://lucene.apache.org/solr/guide/7_1/working-with-dates.html#date-formatting
                index_actions = max(index_actions).date()

            return index_actions

        return obj.last_action_date.date()

    def prepare_bill_type(self, obj):
        return obj.bill_type

    def prepare_text(self, obj):
        return self.text.prepare(obj)

    def prepare(self, obj):
        data = super().prepare(obj)

        boost = 1
        if obj.last_action_date:
            now = app_timezone.localize(datetime.now())

            # obj.last_action_date can be in the future
            weeks_passed = (now - obj.last_action_date).days / 7 + 1
            boost = 1 + 5.0 / max(weeks_passed, 1)

        data['boost'] = boost

        return data
