from unittest.mock import MagicMock

import pytest
from lxml import etree
from haystack.query import SearchQuerySet
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator


# Different combinations of possible parameters
sorters = ['title', 'date', 'relevance', None]
orders = ['asc', 'desc']
queries = ['test', None]

@pytest.mark.django_db
@pytest.mark.parametrize('sort_by', sorters)
@pytest.mark.parametrize('order_by', orders)
@pytest.mark.parametrize('query', queries)
def test_search_params(sort_by, order_by, query, mocker):

    # Use different query strings depending on the params
    if sort_by or order_by or query:
        query_string = '?'
        if sort_by:
            query_string += 'sort_by={sort_by}'.format(sort_by=sort_by)
        if order_by:
            query_string += '&order_by={order_by}'.format(order_by=order_by)
        if query:
            query_string += '&q={query}'.format(query=query)
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

        tree = etree.HTML(search.content.decode('utf-8'))

        # Check that a link with correct text in bold font appears on the page.
        bolded_link, = tree.xpath("//strong/a[contains(@class, 'assort')]")
        assert bolded_link.text.strip() == sort_by.title()

        # Check that the correct sort icon is displayed once. (Relevance doesn't
        # display an icon for order_by.)
        sort_icon, = tree.xpath("//i[contains(@class, 'fa-sort-amount-{}')]".format(order_by))

    elif query or sort_by == 'relevance':
        # When a query exists with no sort_by value, we default
        # to ordering by `relevance` (hence `SearchQuerySet.order_by` will
        # not get called)
        order_func.assert_not_called()
    else:
        # When no query or sort_by values exist, we default to `date` ordering
        assert order_func.call_count == 1
        assert order_func.called_with('-last_action_date')
