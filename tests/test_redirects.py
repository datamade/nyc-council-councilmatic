import pytest

from django.core.urlresolvers import reverse

@pytest.mark.parametrize('correct_slug,malformed_slug,status_code', [
                         ('int-0262-2018', 'int-262-2018', 301),
                         ('int-0262-2018', 'int-262-2018-46fd84ebfff5', 301),
                         ('int-0262-2018', 'int-262', 301),
                         ('int-0262-2018-A', 'int-262-2018-A', 301),
                         ('t2018-1410', 't-2018-1410', 301),
                         ('t2018-1410', 't-2018-1410-46fd84ebfff5', 301),
                         ('t2018-1410', 't-2018-banana', 404),
                         ])
def test_bill_redirects(client, bill, correct_slug, malformed_slug, status_code):
    '''
    This test insures that redirects work for the following cases:
    (1) a slug extended with a UUID
    (2) a slug with missing zeroes
    (3) a slug with an extra hyphen
    (4) a shortened version of a slug

    For all other malformed slugs, the site should return a 404.
    '''
    bill = bill.build(**{'slug': correct_slug})
    url = reverse('bill_detail', kwargs={'slug': malformed_slug})
    response = client.get(url) 

    assert response.status_code == status_code