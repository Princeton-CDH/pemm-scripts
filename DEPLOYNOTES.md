0.5
---

Schema changes require manual updates before re-applying sheet setup
and validation:

- On Story Instance sheet:
   - Add a new column "Body of Story Start" between Line Start and and Folio End


0.4
---

Sheets that should be excluded from sync to GitHub should be renamed to start with an underscore, and their counterpart csv files should be manually removed from `pemm-data`.


0.3
---

This release adds a new column to Story Instance sheet and updates validation across sheets. Manually insert a new column before the Notes field, then run "Set up all sheets" and "Setup validation."


0.2
---

Instructions for converting macomber text file data to CSV,
importing into Google Sheets, and enabling validation:

* Run the conversion script:
`python scripts/macomber_to_csv.py -f data/macomber-miracles.txt -i data/incipits.csv`

* Open the Google Sheets document created by running the
  setup steps in the Readme. Import the CSV files created by the
  conversion script: choose File -> Import, upload file, select file.
  For "import location", choose "Insert new sheet(s)".

* Rename the sheets to *Manuscript*, *Canonical Story*, and
 *Story Instance*

* From the PEMM menu, choose "Set up all sheets"; authorize when prompted.

Instructions for setting up Solr:

* Copy `solr_conf` to Solr configsets directory with name pemm

* Create a new core with that configset: `solr create_core -c pemm -d pemm`

Instructions for setting up Google sheets sync:

* Create credentials based on the [gspread OAuth2 documentation](https://gspread.readthedocs.io/en/latest/oauth2.html) and save the JSON file as pemm_credentials.json

* Make sure to enable both the Google Drive API *and* Google Sheets API in the
  Google developer console.

* Give the email address in the credentials file read access to the
  Google sheet to be synchronized.

* To configure the sync in qa/production, you can set the PEMM_DATA_REPO_PATH,
  PEMM_DATA_REPO_DATADIR, and PEMM_GSHEETS_DOCID environment variables. See the
  module docstring in the `scripts/gsheets_to_git.py` file for more instructions
  and example usage.

