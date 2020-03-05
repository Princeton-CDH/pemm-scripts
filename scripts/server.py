#!/usr/bin/env python
'''
An HTTP server that proxies requests to solr to search for similar incipits.

Run a debug server for development with:
    $ export FLASK_APP=scripts/server.py FLASK_ENV=development
    $ flask run

'''
import os

from flask import Flask, g, jsonify, render_template, request
from parasolr.query import SolrQuerySet
from parasolr.solr.client import SolrClient

from scripts import __version__

# read settings from environment on startup
SOLR_URL = os.getenv('PEMM_SOLR_URL', 'http://localhost:8983/solr/')
SOLR_CORE = os.getenv('PEMM_SOLR_CORE', 'pemm')

# create a new flask app from this module
app = Flask(__name__)


@app.route('/')
def root():
    '''Display version info and a basic html search form.'''
    return render_template('index.html', version=__version__)


@app.route('/search', methods=['GET', 'POST'])
def search():
    '''Search for an incipit and return a list of matching results.'''
    if request.method == 'POST':
        search_term = request.form['incipit']
        output_format = request.form.get('format', '')
    elif request.method == 'GET':
        search_term = request.args.get('incipit', '')
        output_format = request.args.get('format', '')

    queryset = SolrQuerySet(get_solr())
    if search_term:
        queryset = queryset.highlight('incipit_txt_gez', q=search_term,
                                      method='unified', fragsize=0) \
            .search(incipit_txt_gez=search_term) \
            .order_by('-score') \
            .only('id', 'macomber_id_s', 'incipit_txt_gez', 'score')

    results = queryset.get_results()
    if search_term:
        # patch in the highlighted incipits into the main result
        # to avoid accessing separately in the template or json
        highlights = queryset.get_highlighting()
        for i, result in enumerate(results):
            highlighted_incipits = highlights[result['id']]['incipit_txt_gez']
            if highlighted_incipits:
                result['incipit_txt_gez'] = highlighted_incipits[0]

    # if html response was requested, render results.html template
    if output_format == 'html':
        return render_template('results.html', results=results,
                               total=queryset.count(),
                               search_term=search_term)

    # by default, return JSON
    return jsonify(results)


def get_solr():
    '''Get a shared-per-request connection to solr, creating if none exists.'''
    # see https://flask.palletsprojects.com/en/1.1.x/api/#flask.g
    if 'solr' not in g:
        g.solr = SolrClient(SOLR_URL, SOLR_CORE)
    return g.solr
