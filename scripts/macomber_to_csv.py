#!/usr/bin/env python

'''
Convert structured text file based on Macomber's handlist
and CSV of incipits into a set of CSV files for manuscripts,
canonical stories, and story instances.

Input files are included in the data directory

Usage::

    python ./scripts/macomber_to_csv.py -f data/macomber-miracles.txt -i data/incipits.csv

'''


import argparse
import codecs
import csv
import json
import os
import re
from collections import OrderedDict, defaultdict
from datetime import date


SCRIPT_DIR = os.path.dirname(__file__)


class MacomberToCSV:
    '''Convert structured text file based on Macomber handlist
    into a set of related CSV files for use with Google sheets.
    Uses the schema.json file in the scripts directory to
    determine the order of fields in the output.
    '''

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
    # Format for mss ids with a period or dash indicates story order.
    # e.g. 601.141,  681.?, ZBNE 62-30
    mss_id_re = re.compile(
        r'^(?P<id>[^.\s\-()]+)(?P<order>(\.|-)[\d?]+)?( ?\(' +
        folio_regex + r'\))?')

    # translate collection names from the macomber file
    # to the form needed for the spreadsheet
    collection_lookup = {
        'EMDL': 'EMDL (HMML)',
        'EMIP': 'EMIP (HMML)',
        'AECE': 'AECE (HMML)',
        'CBS': 'C-Berlin (BS)',
        'CCBE': 'C-Dublin (CBL)',
        'CF': 'C-Florence (BNCF)',
        'CL': 'C-Leningrad (RAN)',
        'CRA': 'CR-Paris (BNF)',
        'DULE': 'Duke (Duke)',
        'EMML': 'EMML (HMML)',
        'G': 'C-Veroli (BGV)',
        'GBAE': 'G-Milan (BAM)',
        'GVE': 'G-Vatican (BAV)',
        'HBS': 'H-Berlin (BS)',
        'LUE': 'L-Uppsala (UU)',
        'SALE': 'S-Rome (ANL)',
        'SBLE': 'S-London (BL)',
        'SGE': 'S-Paris (BNF)',
        'SWE': 'M-SWE (SWE)',
        'VLVE': 'VL-Vatican (BAV)',
        'WBLE': 'W-London (BM)',
        'PEth': 'PEM (PUL)',
        'ZBNE': 'Z-Paris (BNF)',
        'BM': 'W-London (BM)'
    }

    # manuscript collections with their own field in the input text file
    mss_collections = ['PEth', 'EMIP', 'EMML', 'EMDL']

    # unique set of manuscripts
    manuscripts = defaultdict(set)

    canonical_stories = []
    story_instances = []
    mss_unparsed = []

    # project schema from typescript src directory
    schema_path = os.path.join(SCRIPT_DIR, '..', 'src', 'schema.json')

    # output dir
    output_dir = 'output'

    def __init__(self):
        # load project schema from typescript src
        # NOTE: use ordered dict to ensure order (not guaranteed pre py3.7)
        with open(self. schema_path) as schemafile:
            self.schema = json.load(schemafile, object_hook=OrderedDict)

        # create output directory if it doesn't exist
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

    # nested default dict of dict for incipit lookup
    # - lookup by macomber id, then repository, then manuscript id
    incipits = defaultdict(lambda: defaultdict(dict))

    def load_incipits(self, incipitfile):
        '''Read incipit CSV file into a nested dictionary for lookup
        so that known incipits can be included in the story instance CSV.'''
        with open(incipitfile) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                mac_id, incipit, repository, mss, _ = row
                self.incipits[mac_id][repository][mss] = incipit

    def get_incipit(self, macomber_id, collection, mss_id):
        '''Get incipit text, if present, for an story instance based on
        Macomber id, collection, and manuscript id.'''
        return self.incipits[macomber_id][collection].get(mss_id, '')

    def process_textfile(self, infile, incipitfile):
        '''Process the macomber text file and output CSVs.'''
        record = None
        self.load_incipits(incipitfile)
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
                    # TODO: convert these into a lookup of 1-1 mappings
                    # macomber title
                    if field == 'Title':
                        record['Macomber Title'] = value.strip()
                    elif field == 'Text':
                        record['Print Version'] = value.strip()
                    elif field == 'English translation':
                        record['English Translation'] = value.strip()

                    # combined manuscripts field
                    # these are structured as `collection id (folio)`, e.g.
                    # MSS: CRA 53-17; VLVE 298 (151a).
                    elif field == 'MSS':
                        value = value.strip().strip('.')
                        if value.lower() in ['', 'none']:
                            continue

                        mss_refs = [m.strip() for m in value.split(';')]
                        for mss_ref in mss_refs:
                            # split on first space, if present
                            # remainder
                            # if the manuscript ref starts with an alpha char,
                            # it has a collection id
                            if mss_ref and mss_ref[0].isalpha():
                                if ' ' in mss_ref:
                                    collection, mss = mss_ref.split(' ', 1)
                                elif '-' in mss_ref:
                                    # otherwise split on first dash (e.g. G-1)
                                    collection, mss = mss_ref.split('-', 1)
                                    # special case: these collections each
                                    # have one manuscript only, the number
                                    # is miracle order
                                    # - adjust ref to add mss id 1
                                    mss = '1-%s' % mss
                                else:
                                    # error/warn?
                                    continue
                            # otherwise, collection is inferred
                            # from previous record
                            # e.g. VLVE 267(52b); 272(113a); 298(21b);

                            if collection not in self.collection_lookup:
                                print('warning: bad collection %s / %s' %
                                      (collection, mss_ref))
                            else:
                                self.parse_manuscripts(collection, mss, record)

                    # specific repositories with manuscripts with this story
                    # field is the name of the manuscript repository/collection
                    elif field in self.mss_collections:
                        self.parse_manuscripts(field, value, record)

        self.output_manuscripts()
        self.output_canonical_stories()
        self.output_story_instances()

        if self.mss_unparsed:
            print('Failed to parse these manuscript references:')
            for mss_ref in self.mss_unparsed:
                print(mss_ref)

    def parse_manuscripts(self, collection, manuscripts, canonical_record):
        '''Parse a manuscript reference; add records to the list of
        recognized story instances when the reference can be parsed; add
        to the list of unparsed references when it cannot.

        :param collection: collection abbrevation in the macomber text file
        :param manuscripts: manuscript reference (mss id, folio, etc)
        :param canonical_record: dict with current canonical story details,
            notably macomber id
        '''

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

            # first check for multiple folio notation
            # + or , indicates multiple occurrences within a single manuscript
            if '+' in manuscript or ',' in manuscript:
                # some records have folio numbers in parens
                if '(' not in manuscript:
                    self.mss_unparsed.append(manuscript)
                    continue

                # split manuscript id from list of folio refs
                mss_id, folio_refs = manuscript.split('(', 1)
                mss_id = mss_id.strip()  # remove any whitespace
                # split out each set of folio locations
                folios = re.split(' ?[+,] ?',
                                  folio_refs.strip(')'))
                # add each as a story
                for location in folios:
                    match = self.folio_re.match(location)
                    if match:
                        # pass manuscript id (not included in regex match)
                        self.add_story_instance(
                            collection, canonical_record, match, mss_id)
                    else:
                        # failed to parse one in a multiple
                        self.mss_unparsed.append(
                            '%s %s / %s' % (collection, location, manuscript))

            # not a multiple folio ref
            else:
                match = self.mss_id_re.match(manuscript)
                if match:
                    # add the manuscript id to repository set
                    self.manuscripts[collection].add(match.group('id'))
                    # add a new story instance
                    self.add_story_instance(collection, canonical_record, match)

                else:
                    # failed to parse
                    self.mss_unparsed.append(
                        '%s %s / %s' % (collection, manuscript, manuscripts))

    # make folio notation consistent: convert all "r" to "a", "v" to "b"
    folio_letters = str.maketrans('rv', 'ab')

    def add_story_instance(self, collection, canonical_record, match,
                           mss_id=None):
        '''Add a story instance to the list.  Takes a collection
        abbreviation, current canonical record, regular expression match
        for the manuscript (may include folio start, folio end, and
        manuscript id), and optional manuscript id.'''
        folio_start = match.group('start')
        # folio end should use end if found
        folio_end = match.group('end')
        # for these three collections ONLY, infer folio end = folio start
        # for single page stories (folio end is unknown for others)
        if collection in ['PEth', 'EMDL', 'EMIP'] and not folio_end:
            folio_end = folio_start

        # handle ##rv; repeat start folio number
        if folio_end == 'v':
            folio_end = folio_start.replace('r', 'v')

        # translate rv to ab for consistency
        if folio_start:
            folio_start = folio_start.translate(self.folio_letters)
        if folio_end:
            folio_end = folio_end.translate(self.folio_letters)

        # manuscript id is either passed in or included in regex
        mss_id = mss_id or match.group('id')
        # get incipit if known
        incipit = self.get_incipit(canonical_record['Macomber ID'],
                                   collection, mss_id)
        # order information is included in some MSS ids
        story_order = match.groupdict().get('order', None) or ''
        story_order = story_order.strip('.?-')

        self.story_instances.append({
            # manuscript collection + id
            'Manuscript': '%s %s' %
            (self.collection_lookup.get(collection, collection),
             mss_id),
            'Miracle Number': story_order,
            'Incipit': incipit,
            # imported incipits should be marked as Macomber incipit
            'Macomber Incipit': bool(incipit),  # true if incipit else false
            # mark macomber incipits as high confidence
            'Confidence Score': 'High' if incipit else '',
            'Canonical Story ID': canonical_record['Macomber ID'],
            'Folio Start': folio_start,
            'Folio End': folio_end
        })

    def get_schema_fields(self, sheet_name):
        '''Get a list of field names for the specified sheet from the
        JSON schema'''
        sheet_info = [sheet for sheet in self.schema['sheets']
                      if sheet['name'] == sheet_name][0]
        return [f['name'] for f in sheet_info['fields']]

    def output_filename(self, name):
        '''generate csv output path; files will be created
        in an output directory with current date as prefix.'''
        return os.path.join(self.output_dir,
                            '%s-%s.csv' % (date.today().isoformat(), name))

    def output_canonical_stories(self):
        '''Generate CSV output for canonical stories'''
        # get CSV field names from schema
        fieldnames = self.get_schema_fields('Canonical Story')
        with open(self.output_filename('canonical_stories'), 'w') as csvfile:
            # write utf-8 byte order mark at the beginning of the file
            csvfile.write(codecs.BOM_UTF8.decode())

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.canonical_stories)

    def output_manuscripts(self):
        '''Generate CSV output for manuscripts'''
        fieldnames = self.get_schema_fields('Manuscript')
        with open(self.output_filename('manuscripts'), 'w') as csvfile:
            # write utf-8 byte order mark at the beginning of the file
            csvfile.write(codecs.BOM_UTF8.decode())

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # sort by repository and then by manuscript id,
            # to make this list easier to work with
            for repository in sorted(self.manuscripts.keys()):
                for mss_id in sorted(self.manuscripts[repository]):
                    writer.writerow({
                        'ID': mss_id,
                        # for now, default to value in the file if not found
                        'Collection': self.collection_lookup.get(repository,
                                                                 repository)
                    })

    def output_story_instances(self):
        '''Generate CSV output for story instances'''
        fieldnames = self.get_schema_fields('Story Instance')
        with open(self.output_filename('story_instances'), 'w') as csvfile:
            # write utf-8 byte order mark at the beginning of the file
            csvfile.write(codecs.BOM_UTF8.decode())

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.story_instances)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert PEMM structured text file to CSV.')
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-i', '--incipits', required=True)

    args = parser.parse_args()
    MacomberToCSV().process_textfile(args.file, args.incipits)
