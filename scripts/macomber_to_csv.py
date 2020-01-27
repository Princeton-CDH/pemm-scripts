#!/usr/bin/env python

import argparse
import csv
import json
import os
import re
from collections import OrderedDict, defaultdict


SCRIPT_DIR = os.path.dirname(__file__)


class MacomberToCsv:

    # regex to parse macomber ids in format: MAC0001-A
    macomber_id_re = re.compile(r'^MAC(\d{4})(-[A-F][1-2]?)?')

    # regex to parse manuscript id and folio start/end
    # Typically looks like:
    #   41.6 (18v-19v) or 2233(26a)
    # Also handles rv notation:
    #   46.62 (65rv)
    # Will match on pages with "bis", but currently ignores the bis
    #   2059(20b bis)
    folio_regex = r'(?P<start>\d+[rvab]) ?[-–]? ?(?P<end>(\d+)?[rvab])?( bis)?'
    folio_re = re.compile(folio_regex)
    mss_id_re = re.compile(r'^(?P<id>[\w.]+) ?\(' + folio_regex + r'\)')

    # translate collection names from the macomber file
    # to the form needed for the spreadsheet
    collection_lookup = {
        'PEth': 'PEth (PEth)',    # should this be PUL ?
        'EMIP': 'EMIP (HMML)',
        # 'EMML':
        'EMDL': 'EMDL (HMML)',
    }

    # mss_collections = ['PEth', 'EMIP', 'MSS', 'EMML']
    mss_collections = ['PEth', 'EMIP', 'EMML', 'EMDL']

    # unique set of manuscripts
    manuscripts = defaultdict(set)

    canonical_stories = []
    story_instances = []
    mss_unparsed = []

    # project schema from typescript src directory
    schema_path = os.path.join(SCRIPT_DIR, '..', 'src', 'schema.json')

    def __init__(self):
        # load project schema from typescript src
        # NOTE: use ordered dict to ensure order (not guaranteed pre py3.7)
        with open(self. schema_path) as schemafile:
            self.schema = json.load(schemafile, object_hook=OrderedDict)

    def process_textfile(self, infile):
        record = None
        with open(infile) as txtfile:
            for line in txtfile:
                # macomber id indicates start of a new record
                id_match = self.macomber_id_re.match(line)
                if id_match:
                    # store the previous records, if any, and create new ones
                    if record:
                        self.canonical_stories.append(record)
                    record = {}

                    # convert macomber id to integer (no zero padding) + suffix
                    record['Macomber ID'] = '%s%s' % \
                        (int(id_match.group(1)), id_match.group(2) or '')

                # non-id lines are semi-colon delimited, i.e. field: value
                elif ':' in line:
                    field, value = line.split(':', 1)
                    # macomber title
                    if field == 'Title':
                        record["Macomber Title"] = value.strip()

                    # manuscripts where this story is found;
                    # field is the name of the manuscript repository/collection
                    if field in self.mss_collections:
                        self.parse_manuscripts(field, value, record)

                    # TODO: handle field MSS

        self.output_manuscripts()
        self.output_canonical_stories()
        self.output_story_instances()

        if self.mss_unparsed:
            print('Failed to parse these manuscript references:')
            for mss_ref in self.mss_unparsed:
                print(mss_ref)

    def parse_manuscripts(self, collection, manuscripts, canonical_record):
        # strip whitespace and punctuation we want to ignore
        manuscripts = manuscripts.strip().strip('."')
        # skip if empty or "None"
        if not manuscripts or manuscripts == 'None':
            return

        # split on semicolons and strip whitespace & punctuation
        mss = [m.strip() for m in manuscripts.strip(' .;').split(';')]

        for manuscript in mss:
            # remove any whitespace
            # some records include a title appended to a mss id;
            # strip it out and ignore
            if ':' in manuscript:
                manuscript = manuscript.split(':')[0]

            match = self.mss_id_re.match(manuscript)
            if match:
                # add the manuscript id to repository set
                self.manuscripts[collection].add(match.group('id'))
                # add a new story instance

                folio_start = match.group('start')
                # folio end should use end if found,
                # or start for single-page stories
                folio_end = match.group('end') or folio_start
                # handle ##rv; repeat start folio number
                if folio_end == 'v':
                    folio_end = folio_start.replace('r', 'v')

                self.story_instances.append({
                    # TODO: manuscript id/name
                    'Canonical Story ID': canonical_record['Macomber ID'],
                    # TODO: don't overwrite canonical story title formula
                    'Folio Start': folio_start,
                    'Folio End': folio_end
                })

            # if parsing failed, check for multiple folio notation
            elif '+' in manuscript or ',' in manuscript:
                # if includes + or , indicates multiple occurrences
                # within a single manuscript

                mss_id, folio_refs = manuscript.split('(', 1)
                folios = re.split(' ?[+,] ?',
                                  folio_refs.strip(')'))
                for location in folios:
                    match = self.folio_re.match(location)
                    if match:
                        self.story_instances.append({
                            # TODO: manuscript id/name
                            'Canonical Story ID': canonical_record['Macomber ID'],
                            # TODO: don't overwrite canonical story title formula
                            'Folio Start': match.group('start'),
                            'Folio End': match.group('end') or match.group('start')
                        })

                    else:
                        # failed to parse one in a multiple
                        self.mss_unparsed.append(location)

            else:
                # failed to parse at all
                self.mss_unparsed.append(manuscript)

    def get_schema_fields(self, sheet_name):
        # get field names from JSON schema
        sheet_info = [sheet for sheet in self.schema['sheets']
                      if sheet['name'] == sheet_name][0]
        return [f['name'] for f in sheet_info['fields']]

    def output_canonical_stories(self):
        # get CSV field names from schema
        fieldnames = self.get_schema_fields('Canonical Story')
        with open('canonical_stories.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # NOTE: header should not be written, since we want to append to
            # an existing Google Spreadsheet sheet
            writer.writerows(self.canonical_stories)

    def output_manuscripts(self):
        fieldnames = self.get_schema_fields('Manuscript')
        # FIXME: needs to skip or include formulas for auto-generated fields
        # - name, number of stories
        with open('manuscripts.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # NOTE: header should not be written, since we want to append to
            # an existing Google Spreadsheet sheet
            # TODO: text file repository names need to be converted
            # to collection names in the spreadsheet
            for repository, mss_ids in self.manuscripts.items():
                for mss_id in mss_ids:
                    writer.writerow({
                        'ID': mss_id,
                        # for now, default to value in the file if not found
                        'Collection': self.collection_lookup.get(repository,
                                                                 repository)
                    })

    def output_story_instances(self):
        fieldnames = self.get_schema_fields('Story Instance')
        with open('story_instances.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # NOTE: header should not be written, since we want to append to
            # an existing Google Spreadsheet sheet
            # TODO: text file repository names need to be converted
            # to collection names in the spreadsheet
            writer.writerows(self.story_instances)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert PEMM structured text file to CSV.')
    parser.add_argument('-f', '--file', required=True)

    args = parser.parse_args()
    MacomberToCsv().process_textfile(args.file)
