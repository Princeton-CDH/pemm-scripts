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

* pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib gitpython

* (google sheets api setup/credentials documentation still todo)

* Create or checkout a working copy of the git repository where
 the data  will be stored. It should be configured with a remote
 "origin" for remote synchronization before running the script.


NOTE: currently using unreleased "trix" code for interacting with
Google Sheets; proper release & docs TBD

'''
import argparse
import csv
import os

from git import InvalidGitRepositoryError, Repo
import trix


def sheet_filename(sheetname, mode='csv'):
    '''Generate an output filename based on a sheet name'''
    return '%s.%s' % (sheetname.lower().replace(' ', '_'), mode)


def pad_csv_row(values, size):
    '''add empty strings to make a list of values a specified length'''
    return (values + [''] * (size - len(values)))


def gsheet_to_csv(docid, outdir):
    '''Use Google Sheets API to grab google sheets content for the
    given document and save all sheets as CSV.

    Returns a list of the files created and the name of the document.
    '''
    tsheet = trix.Trix(docid)
    # returns document title followed by list of sheets
    sheetnames = tsheet.getSheets()
    # remove document title
    doctitle = sheetnames.pop(0)
    filenames = []

    # create output directory if it doesn't exist
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    for sheetname in sheetnames:
        filename = os.path.join(outdir, sheet_filename(sheetname))
        filenames.append(filename)
        with open(filename, 'w') as csvfile:
            print('Saving %s as %s' % (sheetname, sheet_filename(sheetname)))
            csvwriter = csv.writer(csvfile)
            sheet_data = tsheet.getRange(sheetname)
            # determine the length of this sheet
            columns = len(sheet_data[0])
            # if rows are equal length, github will display nicely
            csvwriter.writerows([pad_csv_row(row, columns)
                                 for row in sheet_data])

    return (filenames, doctitle)


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Retrieve Google Sheets data as CSV and add to or
    update in a git repository.''')
    parser.add_argument('-d', '--datadir', default='data',
                        help='Data directory within the git repository')
    parser.add_argument('-g', '--gitpath', required=True,
                        help='Git repository working directory')
    parser.add_argument('docid', help='Google Sheets document id')

    args = parser.parse_args()
    filenames, doctitle = gsheet_to_csv(
        args.docid, os.path.join(args.gitpath, args.datadir))
    update_gitrepo(args.gitpath, filenames, doctitle)
