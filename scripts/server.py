#!/usr/bin/env python
'''
An HTTP server that proxies requests to solr to search for similar incipits.

'''
import json

from flask import Flask, render_template, request
from parasolr.solr.client import SolrClient

from . import __version__

SOLR_URL = 'http://localhost:8983/solr/'
SOLR_CORE = 'pemm'

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html', version=__version__)

@app.route('/search', methods=['POST'])
def search():
    # set up solr instance
    solr = SolrClient(SOLR_URL, SOLR_CORE)

    # search for the incipit
    response = solr.query(q='incipit_txt_gez:"%s"' % request.form['incipit'])

    # if html response was requested, render results.html template
    if 'format' in request.form and request.form['format'] == 'html':
        return render_template('results.html', results=response.docs,
                                total=response.numFound)

    # by default, return JSON
    return json.dumps(response.docs)
