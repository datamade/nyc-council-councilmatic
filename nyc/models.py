from django.conf import settings
from councilmatic_core.models import Bill, Organization, Action
from datetime import datetime
import pytz

app_timezone = pytz.timezone(settings.TIME_ZONE)

class NYCBill(Bill):

    class Meta:
        proxy = True

    def __str__(self):
        return self.friendly_name

    # NYC CUSTOMIZATION
    # the date that a bill was passed, if it has been passed
    @property
    def date_passed(self):
        return self.actions.filter(classification='executive-signature').order_by('-order').first().date if self.actions.all() else None

    # NYC CUSTOMIZATION
    # makes a friendly name using bill type & number, e.g. 'Introduction 643-2015'
    # b/c this is how NYC peeps most often refer to a bill
    # this is what is used as the title (heading) for bills throughout the site (bill listing, bill detail)
    @property
    def friendly_name(self):
        nums_only = self.identifier.split(' ')[-1]
        return self.bill_type+' '+nums_only

    # NYC CUSTOMIZATION
    # this is b/c we don't have data on bills voted against, only bills passed -
    # everything else is just left to die silently ¯\_(ツ)_/¯
    # turns out that ~80% of nyc bills that get passed, are passed within
    # 2 months of the last action
    # using 6 months instead of 2 months for cutoff, to minimize incorrectly labeling
    # in-progress legislation as stale
    @property
    def _is_stale(self):
        # stale = no action for 6 months
        last_action = self.actions.order_by('-order').first()

        if last_action and last_action.date:
            timediff = datetime.now().replace(tzinfo=app_timezone) - last_action.date
            return (timediff.days > 150)
        else:
            return True

    # NYC CUSTOMIZATION
    # whether or not a bill has reached its final 'completed' status
    # what the final status is depends on bill type
    @property
    def _terminal_status(self):

        bill_type = self.bill_type
        history = {a.classification: a.description for a in self.actions.all()}

        if history:
            if 'failure' in history.keys():
                if history['failure'] == 'Filed (End of Session)':
                    return 'Expired'
                else:
                   return 'Failed'
            elif bill_type == 'Introduction':
                if 'executive-signature' in history.keys():
                    return 'Enacted'
                else:
                    return False
            elif bill_type in ['Resolution', 'Land Use Application', 'Communication', "Mayor's Message", 'Land Use Call-Up']:
                if 'passage' in history.keys():
                    return 'Approved'
                else:
                    return False
        else:
            return False

    # NYC CUSTOMIZATION
    # whether or not something has an approval among any of this actions
    # planning on using this for a progress bar for bills to lay out all the steps to law & how far it has gotten
    # (e.g. introduced -> approved by committee -> approved by council -> approved by mayor)
    @property
    def _is_approved(self):
        if self.actions:
            return any(['Approved' in a.description for a in self.actions.all()])
        else:
            return False

    # NYC CUSTOMIZATION
    # the 'current status' of a bill, inferred with some custom logic
    # this is used in the colored label in bill listings
    @property
    def inferred_status(self):
        # these are the bill types for which a status doesn't make sense
        if self.bill_type in ['SLR', 'Petition', 'Local Laws 2015']:
            return None
        elif self._terminal_status:
            return self._terminal_status
        elif self._is_stale:
            return 'Inactive'
        else:
            return 'Active'

    # NYC CUSTOMIZATION
    # this is used for the text description of a bill in bill listings
    # the abstract is usually friendlier, so we want to use that whenever it's available,
    # & have the description as a fallback
    def listing_description(self):
        if self.abstract:
            return self.abstract
        else:
            return self.description
