#!/usr/bin/env python

'''
Script to synchronize Google Sheets content to a git repository.

Uses Google Sheets API to grab content from a Google Sheets Spreadsheet.
Each sheet in the document is saved as a CSV file with a filename
based on the sheet name. Those files are then added to the local
git repository, committed (if any changes), and pushed to the remote
origin repository if there is one.

Example use:

    ./scripts/gsheets_to_git.py -g /path/to/local/gitrepo GOOGLE-DOCUMENT-ID

Where GOOGLE-DOCUMENT-ID can be found in the URL when viewing the spreadsheet
you want to sync, looking something like:

1dfr9gE8EeIXaj4XXPwuuo2PtJwIUMM18dKfVN24f86A

Setup:

* Create credentials based on the gspread OAuth2 documentation and save the
 JSON file as pemm_credentials.json
 (https://gspread.readthedocs.io/en/latest/oauth2.html)

* Make sure to enable both the Google Drive API *and* Google Sheets API in the
  Google developer console.

* Give the email address in the credentials file read access to the Google
 sheet to be synchronized.

* Create or checkout a working copy of the git repository where
 the data  will be stored. It should be configured with a remote
 "origin" for remote synchronization before running the script.

'''
import argparse
import csv
import json
import os
from datetime import datetime
from types import SimpleNamespace

from git import InvalidGitRepositoryError, Repo
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests


def sheet_filename(worksheet, mode='csv'):
    '''Generate an output filename based on a sheet name'''
    return '%s.%s' % (worksheet.title.lower().replace(' ', '_'), mode)


def pad_csv_row(values, size):
    '''add empty strings to make a list of values a specified length'''
    return (values + [''] * (size - len(values)))


def init_gsheets_client():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # NOTE: currently assumes credentials are in the directory
    # where the script is being run
    credentials = ServiceAccountCredentials \
        .from_json_keyfile_name('pemm_credentials.json', scope)

    return gspread.authorize(credentials)

# ISO format used for dates
MODIFIED_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def get_document_lastmodified(session, docid, page_token=None):
    # NOTE: we could use google api python client, but it's pretty clunky;
    # instead, using the session with credentials configured by gspread

    # GET https://www.googleapis.com/drive/v3/files/fileId
    get_file_url = 'https://www.googleapis.com/drive/v3/files/%s' % docid
    opts = {
        'fields': 'modifiedTime',
        # will be deprecated in June 2020, but 404s without
        'supportsAllDrives': 'true'
    }
    response = session.get(get_file_url, params=opts)
    if response.status_code == requests.codes.ok:
        # convert to datetime
        # (unfortunately not on py3.7 so can't use from isoformat)
        return datetime.strptime(response.json()['modifiedTime'],
                                 MODIFIED_TIME_FORMAT)


# *** methods for handling information about script last run **


LASTRUN_FILENAME = '.gsheets_to_git'


def lastrun_filename():
    # store script last run information in user's home directory
    return os.path.join(os.path.expanduser('~'), LASTRUN_FILENAME)


def get_lastrun_info():
    # check for information about the last run of this script for this gsheet
    lastrun_file = lastrun_filename()
    if os.path.exists(lastrun_file):
        with open(lastrun_file) as lastrun:
            return json.load(lastrun)


def update_lastrun_info(updates):
    # Update or create last run information file
    lastrun_file = lastrun_filename()
    lastrun_info = get_lastrun_info() or {}
    lastrun_info.update(updates)
    with open(lastrun_file, 'w') as lastrun:
            return json.dump(lastrun_info, lastrun, indent=2)


def gsheet_to_csv(docid, outdir):
    '''Use Google Sheets API to grab google sheets content for the
    given document and save all sheets as CSV.

    Returns a list of the files created and the name of the document.
    '''
    gsheets_client = init_gsheets_client()
    # determine when the document was last modified
    gsheet_lastmod = get_document_lastmodified(gsheets_client.session, docid)
    # check for information about the last run of this script for this gsheet
    lastrun_data = get_lastrun_info()

    # if we have a last modified date, compare against document
    if lastrun_data and docid in lastrun_data['modified']:
        script_lastrun = datetime.strptime(lastrun_data['modified'][docid],
                                           MODIFIED_TIME_FORMAT)
        # if not modified, bail out
        if gsheet_lastmod == script_lastrun:
            print('No changes since last run')
            return

    gsheet = gsheets_client.open_by_key(docid)

    # make sure the output dir exists
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # get all worksheets
    worksheets = gsheet.worksheets()
    filenames = []
    for sheet in worksheets:
        # do NOT synchronize github contributor emails
        if sheet.title == '_contributors':
            continue
        filename = os.path.join(outdir, sheet_filename(sheet))
        filenames.append(filename)
        with open(filename, 'w') as csvfile:
            print('Saving %s as %s' % (sheet.title, sheet_filename(sheet)))
            csvwriter = csv.writer(csvfile)
            sheet_data = sheet.get_all_values()
            # determine the length of this sheet
            columns = len(sheet_data[0])
            # if rows are equal length, github will display nicely
            csvwriter.writerows([pad_csv_row(row, columns)
                                 for row in sheet_data])

    # update the lastrun file with document last modification time
    update_lastrun_info({'modified': {
        docid: gsheet_lastmod.strftime(MODIFIED_TIME_FORMAT)
    }})

    return (filenames, gsheet.title)


def update_gitrepo(repo_path, files, doctitle):
    '''Update the git repository and push changes.'''
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        print('%s is not a valid git repository' % repo_path)
        return

    repo.index.add(files)
    if repo.is_dirty():
        print('Committing changes')
        repo.index.commit('Automatic data updates from %s' % doctitle)

        try:
            origin = repo.remote(name='origin')
            # pull any remote changes
            origin.pull()
            # push data updates
            result = origin.push()
            # output push summary in case anything bad happens
            for pushinfo in result:
                print(pushinfo.summary)
        except ValueError:
            print('No origin repository, unable to push updates')
    else:
        print('No changes')


# default data dir within the git repo
DEFAULT_DATA_DIR = 'data'


def get_env_opts():
    # check for environment variable configuration
    return SimpleNamespace(
        gitpath=os.getenv('PEMM_DATA_REPO_PATH', None),
        datadir=os.getenv('PEMM_DATA_REPO_DATADIR', DEFAULT_DATA_DIR),
        docid=os.getenv('PEMM_GSHEETS_DOCID', None)
    )


def get_cli_args():
    # get command-line arguments
    parser = argparse.ArgumentParser(
        description='''Retrieve Google Sheets data as CSV and add to or
    update in a git repository.''')
    parser.add_argument('-d', '--datadir', default=DEFAULT_DATA_DIR,
                        help='Data directory within the git repository')
    parser.add_argument('-g', '--gitpath', required=True,
                        help='Git repository working directory')
    parser.add_argument('docid', help='Google Sheets document id')

    return parser.parse_args()


if __name__ == "__main__":
    # check environment variables for configuration first
    args = get_env_opts()
    # if not set, use command-line args
    if not args.gitpath or not args.docid:
        args = get_cli_args()

    result = gsheet_to_csv(
        args.docid, os.path.join(args.gitpath, args.datadir))
    # if something was returned, there are changes to commit
    if result:
        filenames, doctitle = result
        update_gitrepo(args.gitpath, filenames, doctitle)
