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

* To use the GitHub co-author functionality, create a sheet with the name
 "_contributors" and these columns: google email, github username, github email

'''
import argparse
import csv
import json
import os
from datetime import datetime
from types import SimpleNamespace

from git import InvalidGitRepositoryError, Repo
from googleapiclient.discovery import build

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def sheet_filename(worksheet, mode='csv'):
    '''Generate an output filename based on a sheet name'''
    return '%s.%s' % (worksheet.title.lower().replace(' ', '_'), mode)


def pad_csv_row(values, size):
    '''add empty strings to make a list of values a specified length'''
    return (values + [''] * (size - len(values)))


class GSheetsToGit:

    # default data dir within the git repo
    DEFAULT_DATA_DIR = 'data'

    # ISO format used for dates
    MODIFIED_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    # filename for last run information (stored in current user's home)
    lastrun_filename = os.path.join(os.path.expanduser('~'), '.gsheets_to_git')

    # list of files generated from spreadsheet data
    updated_filenames = []
    # users who modified the spreadsheet since last run
    modifying_users = set()

    def __init__(self, docid, gitpath, datadir=None):
        self.docid = docid
        self.gitpath = gitpath
        self.datadir = datadir or self.DEFAULT_DATA_DIR
        self.outdir = os.path.join(gitpath, datadir)

        self.init_google_clients()

        # synchronize to local csv
        self.gsheet_to_csv()
        # if there were changes, commit to git
        if self.updated_filenames:
            self.update_gitrepo()

        # if everything succeeded,
        # update the lastrun file with document last modification time
        self.update_lastrun_info({
            'modified': {
                self.docid: self.format_time(self.gsheet_lastmod)
            }})

    def init_google_clients(self):
        '''initialize google drive api and gspread client'''
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']

        # NOTE: currently assumes credentials are in the directory
        # where the script is being run
        credentials = ServiceAccountCredentials \
            .from_json_keyfile_name('pemm_credentials.json', scope)

        # initialize gspread client
        self.gspread = gspread.authorize(credentials)
        # initialize google drive api client
        self.drive_api = build('drive', 'v3', credentials=credentials)

    def get_lastrun_info(self):
        # check for information about the last run of this script
        # load as json if it is exists, returns None otherwise
        if os.path.exists(self.lastrun_filename):
            with open(self.lastrun_filename) as lastrun:
                return json.load(lastrun)

    def update_lastrun_info(self, updates):
        # Update or create last run information file
        lastrun_info = self.get_lastrun_info() or {}
        lastrun_info.update(updates)
        with open(self.lastrun_filename, 'w') as lastrun:
                return json.dump(lastrun_info, lastrun, indent=2)

    def parse_time(self, timestr):
        # convert timestamp string to datetime object
        # (unfortunately can't use py3.7 fromisoformat)
        return datetime.strptime(timestr, self.MODIFIED_TIME_FORMAT)

    def format_time(self, datetimeobj):
        # convert datetime ojbect to string in expected format
        return datetimeobj.strftime(self.MODIFIED_TIME_FORMAT)

    def get_document_lastmodified(self):
        '''use drive File API to get document last modified time'''
        results = self.drive_api.files() \
            .get(fileId=self.docid,
                 supportsAllDrives=True, fields='modifiedTime').execute()
        return self.parse_time(results.get('modifiedTime'))

    def get_modifying_users(self, page_token=None):
        '''Populate a list of emails for users who modified the document
        since thelast time this script ran for this document'''

        revision_fields = ','.join('revisions/%s' % field for field in [
            'modifiedTime', 'lastModifyingUser/emailAddress'])
        fields = 'nextPageToken,%s' % revision_fields

        results = self.drive_api.revisions().list(
            fileId=self.docid, fields=fields, pageToken=page_token).execute()

        # if no last run info, compare with unix zero time
        since_date = self.script_lastrun or datetime.fromtimestamp(0)

        revisions = results.get('revisions')

        # google returns revisions oldest first; reverse the order
        revisions.reverse()
        for revision in revisions:
            if self.parse_time(revision['modifiedTime']) > since_date:
                # possible to have revisions without lastModifyingUser
                if 'lastModifyingUser' in revision:
                    self.modifying_users.add(
                        revision['lastModifyingUser']['emailAddress'])
            else:
                # ignore any revisions before our compare date
                break

        # if there is another page, continue looking for modifying users
        page_token = results.get('nextPageToken', None)
        if page_token:
            self.get_modifying_users(page_token)

    # simple property caching
    _script_lastrun = None

    @property
    def script_lastrun(self):
        # determine the last modification timestamp for the last run
        # of this script on this document

        if self._script_lastrun is None:
            # load information about the last run of this script
            lastrun_data = self.get_lastrun_info()
            # if the file exists, pull out modified value for this docid
            if lastrun_data and self.docid in lastrun_data['modified']:
                self._script_lastrun = self.parse_time(
                    lastrun_data['modified'][self.docid])

        return self._script_lastrun

    def gsheet_to_csv(self):
        '''Use Google Sheets API to grab google sheets content for the
        given document and save all sheets as CSV.  If document has not
        been modified since the last script run, does nothing.

        Stores a list of the files created and document title on the class.
        '''
        # determine when the document was last modified
        self.gsheet_lastmod = self.get_document_lastmodified()

        # if we have a last script run modified date, compare against document
        if self.script_lastrun and self.gsheet_lastmod == self.script_lastrun:
            # if not modified, bail out
            print('No changes since last run')
            return

        self.gsheet = self.gspread.open_by_key(self.docid)

        # make sure the output dir exists
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)

        # get all worksheets
        worksheets = self.gsheet.worksheets()
        for sheet in worksheets:
            # do NOT synchronize github contributor emails,
            # OR other internal sheets indicated by leading underscore
            if sheet.title.startswith('_'):
                continue
            filename = os.path.join(self.outdir, sheet_filename(sheet))
            self.updated_filenames.append(filename)
            with open(filename, 'w') as csvfile:
                print('Saving %s as %s' % (sheet.title, sheet_filename(sheet)))
                csvwriter = csv.writer(csvfile)
                sheet_data = sheet.get_all_values()
                # skip if there is no data
                if not sheet_data:
                    continue

                # determine the number of columns in this sheet
                columns = len(sheet_data[0])
                # if rows are equal length, github will display nicely
                csvwriter.writerows([pad_csv_row(row, columns)
                                     for row in sheet_data
                                     if not empty_row(row)])  # skip if empty

    def update_gitrepo(self):
        '''Update the git repository and push changes.'''
        try:
            repo = Repo(self.gitpath)
        except InvalidGitRepositoryError:
            print('%s is not a valid git repository' % self.gitpath)
            return

        commit_msg = 'Automatic data updates from %s' % self.gsheet.title

        # check for modifying users
        self.get_modifying_users()
        # if there are any, use the spreadsheet to map to github account
        if self.modifying_users:
            # get contributor spreadsheet data as a list of dict
            contributors = self.gsheet.worksheet('_contributors') \
                .get_all_records()
            contributor_lookup = {}
            for contrib in contributors:
                contributor_lookup[contrib['google email']] = contrib

            # construct co-author commit and add to the commit message
            coauthors = []
            coauth_msg = 'Co-authored-by: %(github username)s <%(github email)s>'
            for user in self.modifying_users:
                if user in contributor_lookup:
                    coauthors.append(coauth_msg % contributor_lookup[user])

            commit_msg = '%s\n\n%s' % (commit_msg, '\n'.join(coauthors))

        repo.index.add(self.updated_filenames)
        if repo.is_dirty():
            print('Committing changes')
            repo.index.commit(commit_msg)
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


def empty_row(row):
    '''test if all values in a row are empty (empty string or FALSE)'''
    return all(v in ['', 'FALSE'] for v in row)


def get_env_opts():
    # check for environment variable configuration
    return SimpleNamespace(
        gitpath=os.getenv('PEMM_DATA_REPO_PATH', None),
        datadir=os.getenv('PEMM_DATA_REPO_DATADIR', GSheetsToGit.DEFAULT_DATA_DIR),
        docid=os.getenv('PEMM_GSHEETS_DOCID', None)
    )


def get_cli_args():
    # get command-line arguments
    parser = argparse.ArgumentParser(
        description='''Retrieve Google Sheets data as CSV and add to or
    update in a git repository.''')
    parser.add_argument('-d', '--datadir', default=GSheetsToGit.DEFAULT_DATA_DIR,
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

    # NOTE: arg parsing could probably be better, and could be handled
    # within the class, but leaving as is for now
    GSheetsToGit(args.docid, args.gitpath, args.datadir)
