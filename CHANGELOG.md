# Change log

## 0.5.0

This release was concerned with completing the remaining responsibilities on the current funding cycle, including preliminary research / visualizations, data validation, and final changes to the website. Schema and validation responsibilities were handed off to the full-time PEMM team.

Enhancements
 - Add Recension IDs to results interface
 - Identify "Canonical Incipit" in the results interface

Chores
 - Ignore empty rows when synchronizing Google Sheets data to GitHub

Notes
 - The typescript in src has been retired.
 - The cron job frequency was increased on QA, but on the next deploy it should return to normal.

### pemm-data

 - Develop Slack messaging system and GitHub Actions to summarize goodtables errors whenever new sync occurs 
 - Send Slack message if JSON was not formatted appropriately
 - Ignore the extra columns error.

## 0.4.0

This release prepared data for easier data validation, ignoring empty rows, extra sheets, and setting up the schema for Frictionless Data.

- Adds a JSON version of macomber-miracles.txt.

### Syncing with Google Sheets

- Ignore sheets that begin with an underscore.
- Skip empty rows.

### pemm-data

- Adds Frictionless data package
- GitHub Actions setup to validate CSVs


## 0.3.0

### Google Sheets

- Bind regex validation by current row and column instead of hardcoded cell references
- Use numeric validation instead of regex for latitude/longitude

- Schema changes
	- Rename Macomber Incipit to Canonical Incipit 
	- Expand options for story management choice
	- Include help text in the schema file and automatically add as notes to headers

- Bug fixes
	- Revise Solr IDs to ensure uniqueness to fix missing incipits
	- Fix Manuscript sheet, Date Range field validation
	- Named range is based on the initial number of rows

### Incipit search

- As a researcher, I want a way to exclude high-confidence incipits from the Incipit Tool so that incipits entered with typos or mistakes are not included in the search.

- Show 20 results instead of 10 for incipit search


## 0.2.1

- Spreadsheet validation updates:
  - Correct validation for Manuscript date range start and end
  - Remove validation for Manuscript century
- Correct typos in Ge'ez in incipit search tool


## 0.2

Revised the appscript code to apply validation to an existing Google sheet,
so that data could be converted to CSV and imported without overriding
lookups and data validation.

Includes two scripts meant to be run as cron jobs (sync to GitHub
and index in Solr), and a simple Flask app for searching incipits.

* As a researcher, I want to apply schema and data validation to an existing sheet so I can import data as a starting point.
* As a researcher, I want the structured text file and incipits parsed into canonical stories, story instances, and manuscripts and imported into Google Sheets so I can work with the data in a more structured form.
* As a researcher, I want data from Google Sheets synchronized to a GitHub repository to include contributor information so that people working on the data get credit for their work.
* As a researcher, I want data from Google Sheets automatically synchronized to a GitHub repository in CSV format so that I have a versioned backup of the data.
* As a researcher I want to search on high-confidence incipits so that I can check results that will be used in the sheets incipit lookup tool.
* Various spreadsheet field changes and schema additiosn
* Script to index incipit data in Solr

## 0.1

Initial implementation of appscript code to create a Google sheet
based on a configured schema file, with custom type validation and
data validation across sheets.

* As a google sheets user, I want a spreadsheet generated that matches
  the agreed upon data model and fields for tracking PEMM manuscript data,
  so that I can import and add project data.
    * pull out spreadsheet config into a single data file
    * set up dev environment to support bundling
