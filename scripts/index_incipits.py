#!/usr/bin/env python
'''
Skip to index PEMM incipits in Solr for search.

Requires parasolr:

    pip install parasolr

Create a solr core with the local solr configset for
searching on Geʽez / Fidäl:

    solr create_core -c pemm_incipit -d solr_conf

Run this script, providing solr connection details and a path
to the PEMM project CSV file for story instances.

    python index_incipits.py http://localhost:8983/solr/ pemm_incipit \
        /path/to/data/story_instance.csv

'''

import argparse
import csv

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
        incipit_rows = [row for row in csvreader if row['Incipit']]
        # index macomber id & incipit for any rows with an incipit
        solr.update.index([{
            # identifier required for current Solr config
            'id': '%(Manuscript)s %(Folio Start)s' % row,
            'macomber_id_s': row['Canonical Story ID'],
            'incipit_txt_gez': row['Incipit']
        } for row in incipit_rows])

    print('Indexed %d records with incipits' % len(incipit_rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert PEMM structured text file to CSV.')
    parser.add_argument('solr_url', help='Solr URL')
    parser.add_argument('solr_core', help='Solr core')
    parser.add_argument('csvpath', help='Path to CSV file with incipits')

    args = parser.parse_args()
    index_incipits(args.solr_url, args.solr_core, args.csvpath)
