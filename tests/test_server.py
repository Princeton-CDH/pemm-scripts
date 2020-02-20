from unittest.mock import Mock, patch

from flask import g
import pytest

from scripts import __version__, server

# see the flask docs for an explanation of creating an example test client:
# https://flask.palletsprojects.com/en/1.1.x/testing/#the-testing-skeleton

# see also the docs on mocking the 'g' context object:
# https://flask.palletsprojects.com/en/1.1.x/testing/#faking-resources


@pytest.fixture
def client():
    # FIXME incomplete
    server.app.config['TESTING'] = True

    with server.app.test_client() as client, server.app.app_context():
            yield client


def test_index(client):
    # check home page
    rv = client.get('/')
    assert 'version %s' % __version__ in rv.data.decode()
    assert b'<form action="/search" method="post">' in rv.data
    assert b'<input type="hidden" name="format" value="html"/>' in rv.data
    assert b'<input type="text" name="incipit"' in rv.data


@patch('scripts.server.SolrClient')
def test_get_solr(mocksolrclient, client):
    assert 'solr' not in g
    # should initialize solr client and store in app context global
    server.get_solr()
    assert 'solr' in g
    mocksolrclient.assert_called_with(server.SOLR_URL, server.SOLR_CORE)

    # if called again, should not re-initialize
    mocksolrclient.reset_mock()
    server.get_solr()
    mocksolrclient.assert_not_called()


@patch('scripts.server.SolrQuerySet')
def test_search(mocksolrqueryset, client):
    # create Mock solr client and set in app context
    g.solr = Mock()

    # simulate queryset fluent interface
    mocksqs = mocksolrqueryset.return_value
    for method in ['search', 'order_by', 'only']:
        getattr(mocksqs, method).return_value = mocksqs

    test_solr_docs = [
        {'id': '1-A', 'incipit_txt_gez': 'በእንተ፡ ዘከመ፡ አስተርአየቶ፡'}
    ]
    mocksqs.get_results.return_value = test_solr_docs
    mocksqs.count.return_value = 1

    test_search_string = 'አስተርአየቶ'
    rv = client.post('/search', data=dict(incipit=test_search_string))
    assert rv.get_json() == test_solr_docs
    mocksolrqueryset.assert_called_with(g.solr)

    # request html
    rv = client.post('/search', data=dict(
        incipit=test_search_string, format='html'
    ))
    assert b'Search Results' in rv.data
    assert b'1 result' in rv.data
    # search string set as input value
    assert 'value="%s"' % test_search_string in rv.data.decode()
    assert test_solr_docs[0]['id'] in rv.data.decode()
    assert test_solr_docs[0]['incipit_txt_gez'] in rv.data.decode()

    # also handle GET
    rv = client.get('/search?incipit=%s&format=html' % test_search_string)
    assert b'Search Results' in rv.data
    assert 'value="%s"' % test_search_string in rv.data.decode()
    assert b'1 result' in rv.data
