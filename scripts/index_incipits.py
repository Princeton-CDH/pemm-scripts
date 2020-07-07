#!/usr/bin/env python
'''
Skip to index PEMM incipits in Solr for search.

Requires parasolr:

    pip install parasolr

Create a solr core with the local solr configset for
searching on Geʽez / Fidäl:

    solr create_core -c pemm_incipit -d pemm_incipit

Run this script, providing solr connection details and a path
to the PEMM project CSV file for story instances.

    python index_incipits.py http://localhost:8983/solr/ pemm_incipit \
        /path/to/data/story_instance.csv

'''

import argparse
import csv
import os
from types import SimpleNamespace

from parasolr.solr.client import SolrClient


def index_incipits(solr_url, solr_core, incipitfile):
    '''Connect to Solr, clear the index, and index
    incipits and Macomber ids from the specified CSV file.'''

    solr = SolrClient(solr_url, solr_core)
    # clear the index in case identifiers have changed
    solr.update.delete_by_query('*:*')

    # read incipit csv file and index in Solr
    with open(incipitfile) as csvfile:
        csvreader = csv.DictReader(csvfile)
        incipit_rows = [
            row for row in csvreader
            if (row['Incipit'] and row['Confidence Score'] == 'High' and
                row['Canonical Story ID']) and
            not row.get('Exclude from ITool') == 'TRUE'
        ]
        # index macomber id & incipit for any rows with an incipit
        solr.update.index([{
            # identifier required for current Solr config
            'id': 'Mac%(Canonical Story ID)s %(Manuscript)s %(Folio Start)s' \
                  % row,
            'macomber_id_s': row['Canonical Story ID'],
            'recension_id_s': row['Recension ID'],
            'incipit_txt_gez': row['Incipit'],
            'source_s': '%(Manuscript)s %(Folio Start)s' % row,
        } for row in incipit_rows])

    print('Indexed %d records with incipits' % len(incipit_rows))


def get_env_opts():
    # check for environment variable configuration
    return SimpleNamespace(
        solr_url=os.getenv('PEMM_SOLR_URL', None),
        solr_core=os.getenv('PEMM_SOLR_CORE', None),
        csvpath=os.getenv('PEMM_INCIPIT_CSVPATH', None)
    )


def get_cli_args():
    # get command-line arguments
    parser = argparse.ArgumentParser(
        description='Convert PEMM structured text file to CSV.')
    parser.add_argument('solr_url', help='Solr URL')
    parser.add_argument('solr_core', help='Solr core')
    parser.add_argument('csvpath', help='Path to CSV file with incipits')
    return parser.parse_args()

if __name__ == "__main__":
    # check environment variables for configuration first
    args = get_env_opts()
    # if not set, use command line args
    if not all([args.solr_url, args.solr_core, args.csvpath]):
        args = get_cli_args()

    index_incipits(args.solr_url, args.solr_core, args.csvpath)
