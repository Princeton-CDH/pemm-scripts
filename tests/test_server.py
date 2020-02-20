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
    for method in ['search', 'order_by', 'only', 'highlight']:
        getattr(mocksqs, method).return_value = mocksqs

    test_solr_docs = [
        {'id': '1-A', 'incipit_txt_gez': 'በእንተ፡ ዘከመ፡ አስተርአየቶ፡'}
    ]
    mock_highlighting = {
        '1-A': {
            "incipit_txt_gez": ["<em>ዘከመ</em>፡ ተስእላ፡ ሠለስቱ፡ ደናግል፡"]
        }
    }
    mocksqs.get_results.return_value = test_solr_docs
    mocksqs.count.return_value = 1
    mocksqs.get_highlighting.return_value = mock_highlighting

    test_search_string = 'አስተርአየቶ'
    rv = client.post('/search', data=dict(incipit=test_search_string))
    json_data = rv.get_json()
    assert json_data == test_solr_docs
    # result should use highlighted version of incipit
    assert json_data[0]['incipit_txt_gez'] == \
        mock_highlighting['1-A']['incipit_txt_gez'][0]

    mocksolrqueryset.assert_called_with(g.solr)
    mocksqs.search.assert_called_with(incipit_txt_gez=test_search_string)
    mocksqs.order_by.assert_called_with('-score')
    mocksqs.only.assert_called_with('*', 'score')
    mocksqs.highlight.assert_called_with(
        'incipit_txt_gez', q=test_search_string, method='unified', fragsize=0)

    # request html
    rv = client.post('/search', data=dict(
        incipit=test_search_string, format='html'
    ))
    assert b'Search Results' in rv.data
    assert b'1 result' in rv.data
    # search string set as input value
    assert 'value="%s"' % test_search_string in rv.data.decode()
    assert test_solr_docs[0]['id'] in rv.data.decode()
    # make sure highlighted version is displayed
    assert mock_highlighting['1-A']['incipit_txt_gez'][0] in rv.data.decode()

    # handle GET the same way as POST
    rv = client.get('/search?incipit=%s&format=html' % test_search_string)
    assert b'Search Results' in rv.data
    assert 'value="%s"' % test_search_string in rv.data.decode()
    assert b'1 result' in rv.data
