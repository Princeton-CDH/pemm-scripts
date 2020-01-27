#!/usr/bin/env python

import argparse
import csv
import json
import re
from collections import OrderedDict, defaultdict


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


def macomber_to_csv(infile):
    # load project schema from typescript src
    # TODO: should this path be made relative to script?
    # NOTE: use ordered dict to ensure order (order not guaranteed until py3.7)
    with open('src/schema.json') as schemafile:
        schema = json.load(schemafile, object_hook=OrderedDict)
    # print(schema)

    manuscripts = defaultdict(set)
    # mss_collections = ['PEth', 'EMIP', 'MSS', 'EMML']
    mss_collections = ['PEth', 'EMIP', 'EMML']
    canonical_stories = []
    record = None
    story_instances = []

    mss_unparsed = []

    with open(infile) as txtfile:
        for line in txtfile:
            # macomber id indicates start of a new record
            id_match = macomber_id_re.match(line)
            if id_match:
                # store the previous records, if any, and create new ones
                if record:
                    canonical_stories.append(record)
                record = {}

                # convert macomber id into integer (no zero padding) + suffix
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
                if field in mss_collections:
                    # strip whitespace and punctuation we want to ignore
                    value = value.strip().strip('."')
                    # skip if empty or "None"
                    if not value or value == 'None':
                        continue

                    mss = [m.strip() for m in value.strip(' .;').split(';')]
                    for manuscript in mss:
                        # remove any whitespace
                        # some records include a title appended to a mss id;
                        # strip it out and ignore
                        if ':' in manuscript:
                            manuscript = manuscript.split(':')[0]

                        match = mss_id_re.match(manuscript)
                        if match:
                            # add the manuscript id to repository set
                            manuscripts[field].add(match.group('id'))
                            # add a new story instance

                            folio_start = match.group('start')
                            # folio end should use end if found,
                            # or start for single-page stories
                            folio_end = match.group('end') or folio_start
                            # handle ##rv; repeat start folio number
                            if folio_end == 'v':
                                folio_end = folio_start.replace('r', 'v')

                            story_instances.append({
                                # TODO: manuscript id/name
                                'Canonical Story ID': record['Macomber ID'],
                                # TODO: don't overwrite canonical story title formula
                                'Folio Start': folio_start,
                                'Folio End': folio_end
                            })

                        # if parsing failed, check for multiple folio notation
                        if not match:
                            # if includes + or , indicates multiple occurrences
                            # within a single manuscript
                            if '+' in manuscript or ',' in manuscript:
                                mss_id, folio_refs = manuscript.split('(', 1)
                                folios = re.split(' ?[+,] ?',
                                                  folio_refs.strip(')'))
                                for location in folios:
                                    match = folio_re.match(location)
                                    if match:
                                        story_instances.append({
                                            # TODO: manuscript id/name
                                            'Canonical Story ID': record['Macomber ID'],
                                            # TODO: don't overwrite canonical story title formula
                                            'Folio Start': match.group('start'),
                                            'Folio End': match.group('end') or match.group('start')
                                        })

                            else:
                                mss_unparsed.append(manuscript)

                # TODO: handle field MSS

# PEth: 8.14 (25r-27r); 41.98 (144v-150r); 46.79 (96r-97r); 47.35 (97v-99r);
# EMIP:
# MSS: None
# EMML: 2805 (8la); 1606 (50a).

    # get CSV field names from schema
    canonical_story_schema = [sheet for sheet in schema['sheets']
                              if sheet['name'] == 'Canonical Story'][0]
    with open('canonical_stories.csv', 'w') as csvfile:
        fieldnames = [f['name'] for f in canonical_story_schema['fields']]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # NOTE: header should not be written, since we want to append to
        # an existing Google Spreadsheet sheet
        writer.writerows(canonical_stories)

    manuscript_schema = [sheet for sheet in schema['sheets']
                         if sheet['name'] == 'Manuscript'][0]

    # FIXME: needs to skip or include formulas for auto-generated fields
    # - name, number of stories
    with open('manuscripts.csv', 'w') as csvfile:
        fieldnames = [f['name'] for f in manuscript_schema['fields']]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # NOTE: header should not be written, since we want to append to
        # an existing Google Spreadsheet sheet
        # TODO: text file repository names need to be converted
        # to collection names in the spreadsheet
        for repository, mss_ids in manuscripts.items():
            for mss_id in mss_ids:
                writer.writerow({
                    'ID': mss_id,
                    'Collection': collection_lookup.get(repository, repository)
                })

    story_instance_schema = [sheet for sheet in schema['sheets']
                             if sheet['name'] == 'Story Instance'][0]

    with open('story_instances.csv', 'w') as csvfile:
        fieldnames = [f['name'] for f in story_instance_schema['fields']]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # NOTE: header should not be written, since we want to append to
        # an existing Google Spreadsheet sheet
        # TODO: text file repository names need to be converted
        # to collection names in the spreadsheet
        writer.writerows(story_instances)

    if mss_unparsed:
        print('Failed to parse these manuscript references:')
        for mss_ref in mss_unparsed:
            print(mss_ref)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert PEMM structured text file to CSV.')
    parser.add_argument('-f', '--file', required=True)

    args = parser.parse_args()
    macomber_to_csv(args.file)
