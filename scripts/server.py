#!/usr/bin/env python
'''
An HTTP server that proxies requests to solr to search for similar incipits.

Run a debug server for development with:
    $ export FLASK_APP=scripts/server.py FLASK_ENV=development
    $ flask run

'''
import json
import os

from flask import Flask, render_template, request, g
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

@app.route('/search', methods=['POST'])
def search():
    '''Search for an incipit and return a list of similar results.'''
    response = get_solr().query(q='incipit_txt_gez:"%s"' % request.form['incipit'])

    # if html response was requested, render results.html template
    if 'format' in request.form and request.form['format'] == 'html':
        return render_template('results.html', results=response.docs,
                                total=response.numFound)

    # by default, return JSON
    return json.dumps(response.docs)

def get_solr():
    '''Get a shared-per-request connection to solr, creating if none exists.'''
    # see https://flask.palletsprojects.com/en/1.1.x/api/#flask.g
    if 'solr' not in g:
        g.solr = SolrClient(SOLR_URL, SOLR_CORE)
    return g.solr
