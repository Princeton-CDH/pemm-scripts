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

Setup:

* Create credentials based on the gspread OAuth2 documentation and save the
 JSON file as pemm_credentials.json
 (https://gspread.readthedocs.io/en/latest/oauth2.html)

* Give the email address in the credentials file read access to the Google
 sheet to be synchronized.

* Create or checkout a working copy of the git repository where
 the data  will be stored. It should be configured with a remote
 "origin" for remote synchronization before running the script.

'''
import argparse
import csv
import os
from types import SimpleNamespace

from git import InvalidGitRepositoryError, Repo
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def sheet_filename(worksheet, mode='csv'):
    '''Generate an output filename based on a sheet name'''
    return '%s.%s' % (worksheet.title.lower().replace(' ', '_'), mode)


def pad_csv_row(values, size):
    '''add empty strings to make a list of values a specified length'''
    return (values + [''] * (size - len(values)))


def init_gsheets_client():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    # FIXME: how to specify the path? Relative to script, config/env?
    credentials = ServiceAccountCredentials \
        .from_json_keyfile_name('pemm_credentials.json', scope)
    return gspread.authorize(credentials)


def gsheet_to_csv(docid, outdir):
    '''Use Google Sheets API to grab google sheets content for the
    given document and save all sheets as CSV.

    Returns a list of the files created and the name of the document.
    '''
    gsheets_client = init_gsheets_client()
    gsheet = gsheets_client.open_by_key(docid)

    # get all worksheets
    worksheets = gsheet.worksheets()
    filenames = []
    for sheet in worksheets:
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

    filenames, doctitle = gsheet_to_csv(
        args.docid, os.path.join(args.gitpath, args.datadir))
    update_gitrepo(args.gitpath, filenames, doctitle)
