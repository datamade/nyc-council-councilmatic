from unittest.mock import MagicMock

import pytest
from haystack.query import SearchQuerySet
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator

from nyc.models import NYCBill
from nyc.views import NYCCouncilmaticFacetedSearchView

# Different combinations of possible parameters
sorters = ['title', 'date', 'relevance', None]
ascenders = ['true', None]
queries = ['test', None]

@pytest.mark.django_db
@pytest.mark.parametrize('sort_by', sorters)
@pytest.mark.parametrize('ascending', ascenders)
@pytest.mark.parametrize('query', queries)
def test_search_params(sort_by, ascending, query, mocker):

    # Use different query strings depending on the params
    if sort_by or ascending or query:
        query_string = '?'
        if sort_by:
            query_string += 'sort_by={sort_by}'.format(sort_by=sort_by)
        if ascending:
            query_string += '&ascending={ascending}'.format(ascending=ascending)
        if query:
            query_string += '%q={query}'.format(query=query)
    else:
        query_string = ''

    # Mock the SearchQuerySet.order_by method so we can track how it's used
    sqs = MagicMock(spec=SearchQuerySet)
    empty_qs = sqs
    order_func = sqs.facet().facet().facet().facet().facet().highlight().order_by
    order_func.return_value = empty_qs
    mocker.patch('nyc.views.SearchQuerySet', return_value=sqs)

    # Also mock out the `extra_context` method of the search view, which
    # will try to check to make sure Solr is running otherwise
    mocker.patch('nyc.views.NYCCouncilmaticFacetedSearchView.extra_context', return_value={})

    # The Paginator object gets mad if Solr doesn't return any actual results,
    # so let's mock it out too
    pag = MagicMock(spec=Paginator)
    pag.validate_number.return_value = 0
    mocker.patch('haystack.views.Paginator', return_value=pag)

    client = Client()
    search = client.get(reverse('search') + query_string)

    assert search.status_code == 200

    if sort_by and sort_by != 'relevance':

        # Make sure ordering was applied
        assert order_func.call_count == 1

        # Look for the emphasized button on the page signalling that this
        # ordering key has been selected
        button= '<strong>{sort_by}</strong>'.format(sort_by=sort_by.title())
        assert button in search.content.decode('utf-8')

    elif query or sort_by == 'relevance':
        # When a query exists with no sort_by value, we default
        # to ordering by `relevance` (hence `SearchQuerySet.order_by` will
        # not get called)
        order_func.assert_not_called()
    else:
        # When no query or sort_by values exist, we default to `date` ordering
        assert order_func.call_count == 1
        assert order_func.called_with('-last_action_date')

    # Check that the ascending keyword got handled
    if sort_by and sort_by != 'relevance': # Relevance doesn't display anything for ascending
        if ascending:
            assert 'fa-sort-amount-asc' in search.content.decode('utf-8')
        else:
            if sort_by == 'date':
                # Descending is the default for Date
                assert 'fa-sort-amount-desc' in search.content.decode('utf-8')
            elif sort_by == 'title':
                # Ascending is the default for Title
                assert 'fa-sort-amount-asc' in search.content.decode('utf-8')
