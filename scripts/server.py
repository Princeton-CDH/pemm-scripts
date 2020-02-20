#!/usr/bin/env python
'''
An HTTP server that proxies requests to solr to search for similar incipits.

Run a debug server for development with:
    $ export FLASK_APP=scripts/server.py FLASK_ENV=development
    $ flask run

'''
import os

from flask import Flask, g, jsonify, render_template, request
from parasolr.solr.client import SolrClient

from scripts import __version__

# read settings from environment on startup
SOLR_URL = os.getenv('SOLR_URL', 'http://localhost:8983/solr/')
SOLR_CORE = os.getenv('SOLR_CORE', 'pemm')

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

    response = get_solr().query(q='incipit_txt_gez:"%s"' % search_term)

    # if html response was requested, render results.html template
    if output_format == 'html':
        return render_template('results.html', results=response.docs,
                               total=response.numFound,
                               search_term=search_term)

    # by default, return JSON
    return jsonify(response.docs)


def get_solr():
    '''Get a shared-per-request connection to solr, creating if none exists.'''
    # see https://flask.palletsprojects.com/en/1.1.x/api/#flask.g
    if 'solr' not in g:
        g.solr = SolrClient(SOLR_URL, SOLR_CORE)
    return g.solr
