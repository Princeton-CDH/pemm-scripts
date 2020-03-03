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

* Give the email address in the credentials file read access to the
  Google sheet to be synchronized.





